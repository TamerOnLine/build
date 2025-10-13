# api/errors.py
from __future__ import annotations

import json
import logging
import os
import traceback
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

# -------------------------------------------------------------
# إعدادات عامة
# -------------------------------------------------------------
# استخدم DEBUG=true في البيئة لعرض رسائل أخطاء تفصيلية أثناء التطوير
def _is_debug() -> bool:
    val = os.getenv("DEBUG") or os.getenv("FASTAPI_DEBUG") or os.getenv("APP_DEBUG")
    return str(val).lower() in {"1", "true", "yes", "on"}

DEBUG = _is_debug()

# لو عندك لوجر Uvicorn فاستفد منه ليظهر بنفس تنسيق اللوجات
logger = logging.getLogger("uvicorn.error") if logging.getLogger("uvicorn.error") else logging.getLogger(__name__)


# -------------------------------------------------------------
# شكل استجابة موحّد للأخطاء
# -------------------------------------------------------------
def _make_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
) -> JSONResponse:
    """
    يُرجع استجابة JSON موحّدة للأخطاء بالشكل:
    {
      "ok": false,
      "data": null,
      "error": { "code": "...", "message": "...", "details": {...} },
      "trace_id": "..."
    }
    """
    payload: Dict[str, Any] = {
        "ok": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "trace_id": trace_id,
    }
    return JSONResponse(content=payload, status_code=status_code)


def _get_trace_id(request: Request) -> str:
    """
    نقرأ Trace-ID من الهيدر إن وُجد، أو ننشئ واحدًا.
    """
    # يدعم بعض البروكسي/الـ API Gateway ترويسات مختلفة
    for hdr in ("x-request-id", "x-correlation-id", "x-trace-id"):
        if hdr in request.headers:
            return request.headers[hdr]
    return uuid.uuid4().hex


# -------------------------------------------------------------
# خطأ تطبيق مخصّص يمكنك رفعه من أي مكان في الكود
# -------------------------------------------------------------
class AppError(Exception):
    """
    استخدمه للأخطاء المتوقّعة في منطق العمل (Business Errors).

    raise AppError("PROFILE_NOT_FOUND", "Profile not found.", status_code=404, details={"name": name})
    """
    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


# -------------------------------------------------------------
# مُسجّل معالِجات الاستثناءات في التطبيق
# -------------------------------------------------------------
def register_exception_handlers(app: FastAPI) -> None:
    """
    استدعِ هذه الدالة بعد إنشاء app في main.py لتفعيل معالجات الأخطاء الموحّدة.
    """

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError):
        trace_id = _get_trace_id(request)

        # نسجّل الخطأ، لكن دون Stacktrace مزعج لأنه خطأ متوقّع
        logger.warning(
            "AppError [%s] %s | details=%s | trace_id=%s | path=%s",
            exc.code,
            exc.message,
            exc.details,
            trace_id,
            request.url.path,
        )

        return _make_error_response(
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
            trace_id=trace_id,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(request: Request, exc: StarletteHTTPException):
        trace_id = _get_trace_id(request)

        # أمثلة شائعة: 404/403/401...
        code_map = {
            HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            HTTP_403_FORBIDDEN: "FORBIDDEN",
            HTTP_404_NOT_FOUND: "NOT_FOUND",
            HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMITED",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")

        # نعرض رسالة الخطأ التي مرّرتها FastAPI/Starlette
        msg = exc.detail if isinstance(exc.detail, str) else "HTTP error"

        logger.info(
            "HTTPException %s %s | trace_id=%s | path=%s",
            exc.status_code,
            msg,
            trace_id,
            request.url.path,
        )

        return _make_error_response(
            status_code=exc.status_code,
            code=code,
            message=msg,
            details=None,
            trace_id=trace_id,
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_request_validation(request: Request, exc: RequestValidationError):
        trace_id = _get_trace_id(request)

        # تفاصيل الفاليديشن من Pydantic/FastAPI
        try:
            errors = exc.errors()
        except Exception:
            errors = [{"type": "validation_error", "msg": str(exc)}]

        # نصّ الرسالة الموحّد
        message = "Validation error"

        # عند التطوير نُلحق جسم الطلب ليساعدك على التشخيص
        details: Dict[str, Any] = {"errors": errors}
        if DEBUG:
            try:
                body = await request.body()
                details["request_body"] = body.decode("utf-8") if body else ""
            except Exception:
                pass

        logger.debug(
            "RequestValidationError | trace_id=%s | path=%s | errors=%s",
            trace_id,
            request.url.path,
            errors,
        )

        return _make_error_response(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            trace_id=trace_id,
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(request: Request, exc: Exception):
        trace_id = _get_trace_id(request)

        # في التطوير: نعرض Traceback كامل، في الإنتاج نعرض رسالة عامة فقط
        if DEBUG:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            details = {"traceback": tb, "type": type(exc).__name__}
            # حاول قراءة جسم الطلب للمساعدة في التشخيص
            try:
                body = await request.body()
                # قد يكون JSON أو نص؛ نحاول تحويله
                try:
                    details["request_body"] = json.loads(body.decode("utf-8"))
                except Exception:
                    details["request_body"] = body.decode("utf-8") if body else ""
            except Exception:
                pass
        else:
            details = {}

        logger.error(
            "Unhandled Exception | %s | trace_id=%s | path=%s",
            repr(exc),
            trace_id,
            request.url.path,
            exc_info=True,  # يسجّل الستاك تريس في اللوج
        )

        return _make_error_response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message="An unexpected error occurred." if not DEBUG else str(exc),
            details=details,
            trace_id=trace_id,
        )

