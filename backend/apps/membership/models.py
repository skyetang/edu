from django.db import models
from apps.users.models import User

class MembershipPlan(models.Model):
    UNIT_CHOICES = (
        ("DAY", "天"),
        ("WEEK", "周"),
        ("MONTH", "月"),
        ("YEAR", "年"),
    )
    
    name = models.CharField(max_length=50, verbose_name="会员名称")
    level = models.IntegerField(default=1, verbose_name="会员等级权重")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="原价")
    
    duration_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default="MONTH", verbose_name="有效期单位")
    duration_value = models.IntegerField(default=1, verbose_name="有效期数值")
    duration_days = models.IntegerField(default=30, verbose_name="有效期(天)")
    
    description = models.TextField(blank=True, verbose_name="权限描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "membership_plans"
        ordering = ["level", "price"]
        verbose_name = "会员套餐"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} (Lv.{self.level})"
        
    def save(self, *args, **kwargs):
        # Calculate total days based on unit and value
        multipliers = {
            "DAY": 1,
            "WEEK": 7,
            "MONTH": 30,
            "YEAR": 365
        }
        if self.duration_unit and self.duration_value:
            self.duration_days = self.duration_value * multipliers.get(self.duration_unit, 1)
        super().save(*args, **kwargs)

class MemberOrder(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "待支付"),
        ("PAID", "已支付"),
        ("CANCELLED", "已取消"),
        ("REFUNDED", "已退款"),
        ("EXPIRED", "已过期"),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ("WECHAT", "微信支付"),
        ("ALIPAY", "支付宝"),
    )

    ORDER_TYPE_CHOICES = (
        ("NEW", "新购"),
        ("RENEWAL", "续费"),
        ("UPGRADE", "升级"),
    )

    order_no = models.CharField(max_length=32, unique=True, verbose_name="订单号")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="member_orders", verbose_name="用户")
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True, verbose_name="会员套餐")
    
    # Store snapshot of plan details
    plan_name = models.CharField(max_length=50, verbose_name="套餐名称快照")
    plan_days = models.IntegerField(verbose_name="套餐天数快照")
    
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default="NEW", verbose_name="订单类型")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="实付金额")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="抵扣金额")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", verbose_name="状态")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True, verbose_name="支付方式")
    
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="支付时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "member_orders"
        ordering = ["-created_at"]
        verbose_name = "会员订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Order {self.order_no} - {self.user.phone}"
