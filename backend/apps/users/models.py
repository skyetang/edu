from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("必须提供手机号")
        phone = str(phone)
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True)
    nickname = models.CharField(max_length=50, default="")
    avatar = models.CharField(max_length=255, blank=True, default="")
    level = models.IntegerField(default=1, verbose_name="用户等级")
    membership_expire_at = models.DateTimeField(null=True, blank=True, verbose_name="会员过期时间")
    membership_reference_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="当前会员参考总价")
    membership_reference_days = models.IntegerField(default=0, verbose_name="当前会员参考总天数")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

