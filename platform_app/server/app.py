import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from platform_app.server.services.db import init_db
from platform_app.server.routers import auth, github_setup, registrations, dashboard
from safelane.adapters.github import router as safelane_router

logger = logging.getLogger('safelane.platform')
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
    stream=sys.stdout,
)


# ── OpenTelemetry setup (no-op if OTEL_EXPORTER_OTLP_ENDPOINT not set) ──────
def _setup_otel(app: FastAPI) -> None:
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logger.info("OTEL_EXPORTER_OTLP_ENDPOINT not set — OpenTelemetry disabled.")
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "safelane"),
            "service.version": "2.3.0",
            "deployment.environment": os.environ.get("RAILWAY_ENVIRONMENT", "production"),
        })
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=f"{endpoint.rstrip('/')}/v1/traces",
            headers={"Authorization": f"Bearer {os.environ.get('OTEL_EXPORTER_AUTH_TOKEN', '')}"},
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        logger.info(f"OpenTelemetry tracing enabled → {endpoint}")
    except ImportError:
        logger.warning("opentelemetry packages not installed — tracing skipped.")
    except Exception as e:
        logger.warning(f"OpenTelemetry setup failed (non-fatal): {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="SafeLane — Change Assurance Platform",
    version="2.3.0",
    lifespan=lifespan,
)

# ── OpenTelemetry (must instrument before routes are called) ─────────────────
_setup_otel(app)

# ── CORS ──────────────────────────────────────────────────────────────────────
allowed_origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:8000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Hub-Signature-256", "X-GitHub-Event"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(github_setup.router, prefix="/api/github", tags=["github"])
app.include_router(registrations.router, prefix="/api/registrations", tags=["registrations"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(safelane_router, prefix="/api/safelane", tags=["safelane"])

# Webhook at root for direct GitHub delivery
app.include_router(safelane_router, prefix="", tags=["safelane-compat"], include_in_schema=False)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health")
@app.get("/health/")
async def health_check():
    return {"status": "ok", "service": "safelane-platform", "version": "2.3.0"}


# ── Prometheus /metrics endpoint ─────────────────────────────────────────────
@app.get("/metrics", include_in_schema=False)
async def metrics():
    """Expose Prometheus metrics. Protected by a simple bearer token if METRICS_TOKEN is set."""
    token = os.environ.get("METRICS_TOKEN")
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return Response(content="# prometheus_client not installed\n", media_type="text/plain")


# ── Serve Frontend SPA ────────────────────────────────────────────────────────
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
FRONTEND_LEGACY = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    # Serve Vite build static assets
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the SPA — return index.html for all non-API routes."""
        if full_path.startswith(("api/", "webhook/", "health", "metrics")):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        static_file = FRONTEND_DIST / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))

        return FileResponse(str(FRONTEND_DIST / "index.html"))

elif FRONTEND_LEGACY.exists() and (FRONTEND_LEGACY / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_LEGACY), html=True), name="frontend")
