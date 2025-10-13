# api/main.py
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.errors import register_exception_handlers
from api.settings import get_settings
from api.routes import profiles as profiles_routes
from api.routes import generate_form as gen_routes
from api.routes import meta as meta_routes

settings = get_settings()

API_BASE = f"{settings.api_prefix}/{settings.api_version}"

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

# CORS („‰ «·≈⁄œ«œ«  «·ÃœÌœ…)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# ‰‘— „·›«  profiles/
app.mount(
    settings.public_profiles_mount,
    StaticFiles(directory=str(settings.profiles_dir)),
    name="profiles",
)

# «·—«Ê —« 
app.include_router(profiles_routes.router, prefix=API_BASE, tags=["profiles"])
app.include_router(gen_routes.router,      prefix=API_BASE, tags=["forms"])
app.include_router(meta_routes.router,     prefix=API_BASE, tags=["meta"])

# „⁄«·Ã«  «·√Œÿ«¡
register_exception_handlers(app)

# ’Õ¯… «·Œœ„…
@app.get("/healthz")
def healthz():
    return {"ok": True, "status": "healthy"}

@app.get("/")
def root():
    return {
        "ok": True,
        "message": "API is running",
        "profiles_dir": str(settings.profiles_dir),
        "public_mount": settings.public_profiles_mount,
        "api_base": API_BASE,
    }

