from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated

def ok(data=None, message="操作成功", meta=None, request_id=None, status=200):
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
    
    # Force 401 for Authentication exceptions even if they were mapped to 403
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        if response is None:
             # Should not happen if DRF handled it, but just in case
             pass
        else:
             response.status_code = 401

    if response is not None:
        detail = None
        if isinstance(response.data, dict):
            detail = response.data.get("detail")
        message = detail or str(exc)
        
        code = "SERVER_ERROR"
        if response.status_code in (400, 422):
            code = "VALIDATION_ERROR"
        elif response.status_code == 401:
            code = "AUTH_EXPIRED"
        elif response.status_code == 403:
            code = "PERMISSION_DENIED"
        elif response.status_code == 404:
            code = "NOT_FOUND"
        elif response.status_code == 429:
            code = "RATE_LIMITED"
            
        response.data = {
            "success": False,
            "code": code,
            "message": message,
            "data": None,
            "meta": None,
            "request_id": request_id,
        }
    return response

