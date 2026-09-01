import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from platform_app.server.services.db import init_db
from platform_app.server.routers import auth, github_setup, registrations, dashboard
from safelane.adapters.github import router as safelane_router

logger = logging.getLogger('safelane.platform')
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    await init_db()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="SafeLane — Change Assurance Platform",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──
allowed_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ──
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(github_setup.router, prefix="/api/github", tags=["github"])
app.include_router(registrations.router, prefix="/api/registrations", tags=["registrations"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(safelane_router, prefix="/api/safelane", tags=["safelane"])

# Also mount the webhook at root /webhook/pr for backward compatibility
app.include_router(safelane_router, prefix="", tags=["safelane-compat"], include_in_schema=False)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "safelane-platform", "version": "2.0.0"}


# ── Serve Frontend SPA ──
# Try Vite build output first, then fall back to legacy HTML
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
FRONTEND_LEGACY = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    # Serve static assets from Vite build
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve the SPA — return index.html for all non-API routes."""
        # Don't intercept API routes
        if full_path.startswith("api/") or full_path.startswith("webhook/"):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Try serving static file first
        static_file = FRONTEND_DIST / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))

        # Fallback to index.html for client-side routing
        return FileResponse(str(FRONTEND_DIST / "index.html"))

elif FRONTEND_LEGACY.exists() and (FRONTEND_LEGACY / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_LEGACY), html=True), name="frontend")
