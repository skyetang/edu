from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from .serializers import SendCodeSerializer, RegisterSerializer, LoginPasswordSerializer, LoginCodeSerializer
from .services import send_code, verify_code
from .models import User
from .jwt import issue_token
from config.response import ok, error


class SendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = SendCodeSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        phone = s.validated_data["phone"]
        scene = s.validated_data["scene"]
        if scene == "register" and User.objects.filter(phone=phone).exists():
            return error("CONFLICT", "手机号已注册", status=409)
        ok_send = send_code(phone, scene)
        if not ok_send:
            return error("RATE_LIMITED", "请求过于频繁", status=429)
        return ok({"sent": True})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        phone = s.validated_data["phone"]
        code = s.validated_data["code"]
        password = s.validated_data["password"]
        if not verify_code(phone, "register", code):
            return error("VALIDATION_ERROR", "验证码无效", status=422)
        if User.objects.filter(phone=phone).exists():
            return error("CONFLICT", "手机号已注册", status=409)
        user = User.objects.create(phone=phone, password=make_password(password))
        token = issue_token(user.id, user.phone)
        return ok({"token": token, "user": {"id": user.id, "phone": user.phone}})


class LoginPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginPasswordSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        phone = s.validated_data["phone"]
        password = s.validated_data["password"]
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return error("NOT_FOUND", "用户不存在", status=404)
        if not user.check_password(password):
            return error("AUTH_EXPIRED", "认证失败", status=401)
        token = issue_token(user.id, user.phone)
        return ok({"token": token, "user": {"id": user.id, "phone": user.phone}})


class LoginCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = LoginCodeSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        phone = s.validated_data["phone"]
        code = s.validated_data["code"]
        if not verify_code(phone, "login", code):
            return error("VALIDATION_ERROR", "验证码无效", status=422)
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            user = User.objects.create(phone=phone)
        token = issue_token(user.id, user.phone)
        return ok({"token": token, "user": {"id": user.id, "phone": user.phone}})

