# ──────────────────────────────────────────────────────────────
# Stage 1: Build the React + Vite frontend
# ──────────────────────────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY platform_app/frontend/package*.json ./
RUN npm ci --silent
COPY platform_app/frontend/ ./
# VITE_API_BASE_URL is intentionally left empty so the SPA uses
# relative paths — the FastAPI backend serves it at the same origin.
RUN npm run build

# ──────────────────────────────────────────────────────────────
# Stage 2: Python backend
# ──────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full source
COPY . .

# Copy the Vite build output into the location the app serves from
COPY --from=frontend-builder /frontend/dist ./platform_app/frontend/dist

# Expose the application port
EXPOSE 8000

# ── Entry point with dynamic $PORT expansion for Railway ───────
CMD uvicorn platform_app.server.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
