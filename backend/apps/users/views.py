import random
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .serializers import (
    SendCodeSerializer, RegisterSerializer, LoginPasswordSerializer, 
    LoginCodeSerializer, UserSerializer, PasswordChangeSerializer,
    ChangePhoneStep1Serializer, ChangePhoneStep2Serializer, RefreshTokenSerializer
)
from .services import send_code, verify_code
from .models import User
from config.response import ok, error


def generate_random_nickname():
    """Generate a random nickname: User + 6 digits
    生成随机昵称：User + 6位数字
    """
    return "User" + "".join([str(random.randint(0, 9)) for _ in range(6)])


class SendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = SendCodeSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        phone = s.validated_data["phone"]
        scene = s.validated_data["scene"]

        # 处理更换手机号（旧手机号验证）时的掩码手机号
        if scene == "change_phone_old":
            if request.user and request.user.is_authenticated:
                phone = request.user.phone
            elif "*" in phone:
                 return error("AUTH_EXPIRED", "请先登录", status=401)

        if scene == "register" and User.objects.filter(phone=phone).exists():
            return error("CONFLICT", "手机号已注册", status=409)
        if scene == "change_phone_new" and User.objects.filter(phone=phone).exists():
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
        
        nickname = generate_random_nickname()
        while User.objects.filter(nickname=nickname).exists():
             nickname = generate_random_nickname()

        user = User.objects.create(phone=phone, password=make_password(password), nickname=nickname)
        
        refresh = RefreshToken.for_user(user)
        return ok({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user, context={"request": request}).data
        })


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
        
        refresh = RefreshToken.for_user(user)
        return ok({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user, context={"request": request}).data
        })


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
            nickname = generate_random_nickname()
            while User.objects.filter(nickname=nickname).exists():
                 nickname = generate_random_nickname()
            user = User.objects.create(phone=phone, nickname=nickname)
        
        refresh = RefreshToken.for_user(user)
        return ok({
            "token": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user, context={"request": request}).data
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 使用 SimpleJWT 的 TokenRefreshSerializer 来处理验证和旋转
        # 它将返回 'access' 和 'refresh'（如果 ROTATE_REFRESH_TOKENS 为 True）
        serializer = TokenRefreshSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError) as e:
             return error("AUTH_EXPIRED", "无效的刷新令牌", status=401)
        except Exception as e:
             return error("VALIDATION_ERROR", str(e), status=422)
             
        # 统一响应格式
        return ok(serializer.validated_data)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return ok(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        user = request.user
        s = UserSerializer(user, data=request.data, partial=True, context={"request": request})
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        s.save()
        return ok(s.data)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = PasswordChangeSerializer(data=request.data)
        if not s.is_valid():
             return error("VALIDATION_ERROR", "参数错误", status=422)
        
        user = request.user
        if not user.check_password(s.validated_data["old_password"]):
             return error("VALIDATION_ERROR", "旧密码错误", status=422)
        
        user.set_password(s.validated_data["new_password"])
        user.save()
        return ok(message="密码修改成功")


class VerifyPhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ChangePhoneStep1Serializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        
        code = s.validated_data["code"]
        user = request.user
        if not verify_code(user.phone, "change_phone_old", code):
            return error("VALIDATION_ERROR", "验证码错误", status=422)
        
        key = f"phone_change_verified:{user.id}"
        cache.set(key, True, timeout=600)
        
        return ok(message="验证成功，请绑定新手机号")


class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = ChangePhoneStep2Serializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", "参数错误", status=422)
        
        key = f"phone_change_verified:{request.user.id}"
        if not cache.get(key):
             return error("PERMISSION_DENIED", "请先验证原手机号", status=403)
        
        new_phone = s.validated_data["phone"]
        code = s.validated_data["code"]
        
        if User.objects.filter(phone=new_phone).exists():
             return error("CONFLICT", "手机号已注册", status=409)
             
        if not verify_code(new_phone, "change_phone_new", code):
             return error("VALIDATION_ERROR", "验证码错误", status=422)
             
        user = request.user
        user.phone = new_phone
        user.save()
        
        cache.delete(key)
        
        return ok({"user": UserSerializer(user, context={"request": request}).data}, message="手机号修改成功")


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get("avatar")
        if not file:
            return error("VALIDATION_ERROR", "请选择文件", status=422)
        
        # 暂时使用简单的本地保存
        # 在生产环境中，请使用 OSS 或适当的媒体存储
        import os
        from django.conf import settings
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        # 限制文件大小（例如 2MB）
        if file.size > 2 * 1024 * 1024:
            return error("VALIDATION_ERROR", "文件大小不能超过2MB", status=422)
        
        # 验证文件扩展名
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
             return error("VALIDATION_ERROR", "仅支持图片文件", status=422)

        file_name = f"avatars/{request.user.id}_{int(random.random()*10000)}{ext}"
        path = default_storage.save(file_name, ContentFile(file.read()))
        
        # 保存相对路径到数据库
        user = request.user
        user.avatar = path
        user.save()
        
        # 返回绝对URL用于立即显示
        url = request.build_absolute_uri(settings.MEDIA_URL + path)
        
        return ok({"url": url})
