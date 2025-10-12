# main.py
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ============================
# إعدادات المسارات
# ============================
# مجلد الحفظ الافتراضي: جذر المشروع /profiles
PROFILES_DIR = Path(os.getenv("PROFILES_DIR", str(Path.cwd() / "profiles"))).resolve()
PUBLIC_PROFILES_MOUNT = os.getenv("PUBLIC_PROFILES_MOUNT", "/profiles")

PROFILES_DIR.mkdir(parents=True, exist_ok=True)

# ============================
# تطبيق FastAPI
# ============================
app = FastAPI(title="Resume Builder API", version="1.0.0")

# CORS (عدّل origins حسب واجهتك)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",  # للتطوير فقط
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# تقديم ملفات مجلد الحفظ
# ============================
# أي صورة محفوظة كـ profiles/<name>.png ستظهر على:
# http://localhost:8000/profiles/<name>.png
app.mount(PUBLIC_PROFILES_MOUNT, StaticFiles(directory=str(PROFILES_DIR)), name="profiles")

# ============================
# الراوترات
# ============================
# اختر الاستيراد المناسب لمسار مشروعك:
from api.routes import profiles as profiles_routes  # إذا كان المسار api/routes/profiles.py
# من الممكن أن يكون: from build.api.routes import profiles as profiles_routes

app.include_router(profiles_routes.router, prefix="/api")

# ============================
# صحّة الخدمة
# ============================
@app.get("/")
def root():
    return {
        "ok": True,
        "message": "API is running",
        "profiles_dir": str(PROFILES_DIR),
        "public_mount": PUBLIC_PROFILES_MOUNT,
    }
