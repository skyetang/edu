from rest_framework.response import Response
from rest_framework.views import exception_handler


def ok(data=None, message="ok", meta=None, request_id=None, status=200):
    return Response({
        "success": True,
        "code": "OK",
        "message": message,
        "data": data,
        "meta": meta,
        "request_id": request_id,
    }, status=status)


def error(code, message, data=None, meta=None, request_id=None, status=400):
    return Response({
        "success": False,
        "code": code,
        "message": message,
        "data": data,
        "meta": meta,
        "request_id": request_id,
    }, status=status)


def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", None)
    if response is not None:
        detail = None
        if isinstance(response.data, dict):
            detail = response.data.get("detail")
        message = detail or str(exc)
        code = "VALIDATION_ERROR" if response.status_code in (400, 422) else "SERVER_ERROR"
        response.data = {
            "success": False,
            "code": code,
            "message": message,
            "data": None,
            "meta": None,
            "request_id": request_id,
        }
    return response

