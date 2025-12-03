from rest_framework import serializers


class SendCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    scene = serializers.ChoiceField(choices=["register", "login", "change_phone_old", "change_phone_new"])


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(min_length=6)


class LoginPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField()


class LoginCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    confirm_password = serializers.CharField(min_length=6)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("两次输入的密码不一致")
        return data


class ChangePhoneStep1Serializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class ChangePhoneStep2Serializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    level_display = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        from .models import User
        model = User
        fields = ["id", "phone", "nickname", "avatar", "level", "level_display", "date_joined", "is_staff", "membership_expire_at"]
        read_only_fields = ["id", "phone", "level", "date_joined", "is_staff", "membership_expire_at"]

    def get_level_display(self, obj):
        if obj.is_staff or obj.is_superuser:
            return "管理员"
            
        from django.utils import timezone
        if obj.membership_expire_at and obj.membership_expire_at > timezone.now():
            try:
                from apps.membership.models import MembershipPlan
                plan = MembershipPlan.objects.filter(level=obj.level).first()
                if plan:
                    return plan.name
            except ImportError:
                pass
            return f"VIP Lv.{obj.level}"
            
        return "普通用户"

    def get_avatar(self, obj):
        if not obj.avatar:
            return ""
        if obj.avatar.startswith("http"):
            return obj.avatar
        # Build absolute URL for relative paths
        request = self.context.get("request")
        if request:
            from django.conf import settings
            return request.build_absolute_uri(settings.MEDIA_URL + obj.avatar)
        return obj.avatar

    def get_phone(self, obj):
        if not obj.phone:
            return ""
        # Mask the middle 4 digits if it's an 11-digit phone number
        # 如果是11位手机号，则掩盖中间4位数字
        if len(obj.phone) == 11:
            return f"{obj.phone[:3]}****{obj.phone[7:]}"
        return obj.phone
