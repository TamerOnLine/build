from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.errors import register_exception_handlers
from api.routes import generate_form as gen_routes
from api.routes import meta as meta_routes
from api.routes import profiles as profiles_routes
from api.settings import get_settings

settings = get_settings()
API_BASE = f"{settings.api_prefix}/{settings.api_version}"

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Mount profiles directory
app.mount(
    settings.public_profiles_mount,
    StaticFiles(directory=str(settings.profiles_dir)),
    name="profiles",
)

# Include routers
app.include_router(profiles_routes.router, prefix=API_BASE, tags=["profiles"])
app.include_router(gen_routes.router, prefix=API_BASE, tags=["forms"])
app.include_router(meta_routes.router, prefix=API_BASE, tags=["meta"])
app.include_router(profiles_routes.router, prefix=settings.api_prefix, tags=["profiles-compat"])

# Error handlers
register_exception_handlers(app)

# Health endpoint
@app.get("/healthz")
def healthz():
    return {"ok": True, "status": "healthy"}

# Redirect /generate-form-simple (for backward compat)
@app.post("/generate-form-simple")
async def redirect_generate_form_simple():
    return RedirectResponse(url=f"{API_BASE}/generate-form-simple", status_code=307)

# ✅ Unified root route
@app.get("/")
async def root():
    """Redirect root to docs for convenience."""
    return RedirectResponse(url=f"{API_BASE}/docs")
