from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import MembershipPlan, MemberOrder

class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = "__all__"

class MemberOrderSerializer(serializers.ModelSerializer):
    plan_detail = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)
    remaining_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberOrder
        fields = "__all__"
        read_only_fields = [
            "order_no", "user", "plan_name", "plan_days", 
            "amount", "status", "paid_at", "created_at", "updated_at"
        ]

    def get_plan_detail(self, obj):
        return {
            "name": obj.plan_name,
            "days": obj.plan_days
        }

    def get_remaining_seconds(self, obj):
        if obj.status != 'PENDING':
            return 0
        expire_time = obj.created_at + timedelta(minutes=30)
        now = timezone.now()
        remaining = (expire_time - now).total_seconds()
        return max(0, int(remaining))
