import uuid
import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from config.response import ok, error
from .models import MembershipPlan, MemberOrder
from .serializers import MembershipPlanSerializer, MemberOrderSerializer
from .services import check_and_expire_order
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from decimal import Decimal

User = get_user_model()

class PlanManageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Admin sees all, others see active only
        if request.user.is_authenticated and request.user.is_staff:
            plans = MembershipPlan.objects.all()
        else:
            plans = MembershipPlan.objects.filter(is_active=True)
        return ok(MembershipPlanSerializer(plans, many=True).data)

    def post(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            user_desc = f"User {request.user.phone}" if request.user.is_authenticated else "Anonymous"
            return error("PERMISSION_DENIED", f"无权操作: {user_desc}", status=403)
        
        s = MembershipPlanSerializer(data=request.data)
        if not s.is_valid():
            return error("VALIDATION_ERROR", s.errors, status=422)
        s.save()
        return ok(s.data)

    def patch(self, request):
        if not request.user.is_staff:
            return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone} is_staff={request.user.is_staff}", status=403)
        
        try:
            plan = MembershipPlan.objects.get(id=request.data.get("id"))
        except MembershipPlan.DoesNotExist:
            return error("NOT_FOUND", "套餐不存在", status=404)
            
        s = MembershipPlanSerializer(plan, data=request.data, partial=True)
        if not s.is_valid():
            return error("VALIDATION_ERROR", s.errors, status=422)
        s.save()
        return ok(s.data)
    
    def put(self, request):
        return self.patch(request)
    
    def delete(self, request):
        if not request.user.is_staff:
            return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone} is_staff={request.user.is_staff}", status=403)
        
        try:
            plan = MembershipPlan.objects.get(id=request.query_params.get("id"))
            
            # Check if any orders exist for this plan
            # 检查是否存在关联订单
            if MemberOrder.objects.filter(plan=plan).exists():
                # Soft delete: just set inactive
                # 软删除：仅设置为停用
                plan.is_active = False
                plan.save()
                return ok(message="套餐包含历史订单，已将其下架（停用）而非物理删除")
            
            plan.delete()
            return ok(message="删除成功")
        except MembershipPlan.DoesNotExist:
            return error("NOT_FOUND", "套餐不存在", status=404)

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        try:
            plan = MembershipPlan.objects.get(id=plan_id, is_active=True)
        except MembershipPlan.DoesNotExist:
            return error("NOT_FOUND", "套餐无效或已下架", status=404)
        
        user = request.user
        
        # Use transaction and lock to prevent race condition
        # 使用事务和锁防止竞态条件
        with transaction.atomic():
            # Lock the user record (or a dummy record) to serialize order creation for this user
            # 锁定用户记录以串行化该用户的订单创建
            # We select the user for update to ensure no other transaction can process order creation for this user simultaneously
            _lock = User.objects.select_for_update().get(id=user.id)
            
            order_type = "NEW"
            discount_amount = 0
            amount = plan.price
            
            # Determine Order Type
            is_vip = user.membership_expire_at and user.membership_expire_at > timezone.now()
            
            if is_vip:
                if user.level == plan.level:
                    order_type = "RENEWAL"
                elif user.level < plan.level:
                    order_type = "UPGRADE"
                    # Calculate Upgrade Discount
                    # Formula: Remaining Value = (Reference Amount / Reference Days) * Remaining Days
                    if user.membership_reference_days > 0:
                        remaining_days = (user.membership_expire_at - timezone.now()).days
                        if remaining_days > 0:
                            daily_rate = Decimal(str(user.membership_reference_amount)) / Decimal(user.membership_reference_days)
                            discount_amount = round(daily_rate * Decimal(remaining_days), 2)
                            
                            # Discount cannot exceed plan price
                            if discount_amount > plan.price:
                                discount_amount = plan.price
                            
                            amount = plan.price - discount_amount
                else:
                     return error("VALIDATION_ERROR", "不支持降级购买", status=422)
            
            # Check for existing pending orders
            # 1. Find all pending orders for this user
            pending_orders = MemberOrder.objects.filter(user=user, status="PENDING")
            has_valid_pending_order = False
            
            for pending_order in pending_orders:
                # 2. Check if expired (this function updates status to EXPIRED if timed out)
                is_expired = check_and_expire_order(pending_order)
                if not is_expired:
                    # If not expired, it means it's still valid and pending
                    has_valid_pending_order = True
                    break
            
            if has_valid_pending_order:
                return error("VALIDATION_ERROR", "您存在未支付的订单，请先支付或取消后再下单", status=422)

            # Create Pending Order
            order_no = f"VIP{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"
            
            order = MemberOrder.objects.create(
                order_no=order_no,
                user=user,
                plan=plan,
                plan_name=plan.name,
                plan_days=plan.duration_days,
                amount=amount,
                discount_amount=discount_amount,
                order_type=order_type,
                status="PENDING"
            )
        
        return ok(MemberOrderSerializer(order).data)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_no = request.query_params.get("order_no")
        try:
            order = MemberOrder.objects.get(order_no=order_no)
            if not request.user.is_staff and order.user != request.user:
                return error("PERMISSION_DENIED", "无权查看此订单", status=403)
            
            # Check and expire if necessary
            check_and_expire_order(order)
            
            return ok(MemberOrderSerializer(order).data)
        except MemberOrder.DoesNotExist:
            return error("NOT_FOUND", "订单不存在", status=404)

class OrderPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_no = request.data.get("order_no")
        payment_method = request.data.get("payment_method")
        
        try:
            order = MemberOrder.objects.get(order_no=order_no)
            if order.user != request.user:
                return error("PERMISSION_DENIED", "无权支付他人订单", status=403)
        except MemberOrder.DoesNotExist:
            return error("NOT_FOUND", "订单不存在", status=404)
        
        # Check expiration first (and update status if expired)
        if check_and_expire_order(order):
            return error("VALIDATION_ERROR", "订单已过期", status=422)
            
        if order.status != "PENDING":
            return error("VALIDATION_ERROR", "订单状态不可支付", status=422)

        # Mock Payment Process
        with transaction.atomic():
            # 1. Update Order
            order.status = "PAID"
            order.payment_method = payment_method
            order.paid_at = timezone.now()
            order.save()
            
            # 2. Update User Membership
            user = request.user
            
            if not order.plan:
                 # Should not happen normally if plan is just soft-deleted
                 # If hard deleted, we cannot retrieve level info unless snapshotted.
                 # For now, fail safe.
                 raise ValueError("订单关联套餐已不存在")

            if order.order_type == "NEW":
                user.level = order.plan.level
                user.membership_expire_at = timezone.now() + timedelta(days=order.plan_days)
                user.membership_reference_amount = order.amount
                user.membership_reference_days = order.plan_days

            elif order.order_type == "RENEWAL":
                current_expire = user.membership_expire_at
                if current_expire and current_expire > timezone.now():
                    user.membership_expire_at = current_expire + timedelta(days=order.plan_days)
                else:
                    user.membership_expire_at = timezone.now() + timedelta(days=order.plan_days)
                
                user.membership_reference_amount += order.amount
                user.membership_reference_days += order.plan_days

            elif order.order_type == "UPGRADE":
                user.level = order.plan.level
                user.membership_expire_at = timezone.now() + timedelta(days=order.plan_days)
                # Reset Reference to the full value of the new plan
                # Since we used the old value as discount, effectively we 'bought' the new plan 
                # partially with cash and partially with old value.
                # So the new reference value should be the plan price (or amount + discount).
                user.membership_reference_amount = order.amount + order.discount_amount
                user.membership_reference_days = order.plan_days
                
            user.save()
            
        return ok(message="支付成功，会员已开通")

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Admin sees all, User sees own
        scope = request.query_params.get("scope")
        if request.user.is_staff and scope != 'my':
            orders = MemberOrder.objects.all().order_by('-created_at')
        else:
            orders = MemberOrder.objects.filter(user=request.user).order_by('-created_at')
            
        return ok(MemberOrderSerializer(orders, many=True).data)

class OrderActionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        order_no = request.data.get("order_no")
        action = request.data.get("action") # cancel, refund
        
        try:
            order = MemberOrder.objects.get(order_no=order_no)
        except MemberOrder.DoesNotExist:
            return error("NOT_FOUND", "订单不存在", status=404)
            
        # Cancel logic
        if action == "cancel":
            # Check expiration first
            if check_and_expire_order(order):
                return error("VALIDATION_ERROR", "订单已过期，不可取消", status=422)

            if order.status != "PENDING":
                return error("VALIDATION_ERROR", "当前状态不可取消", status=422)
            # Admin can cancel anyone's, User can only cancel own
            if not request.user.is_staff and order.user != request.user:
                return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone}", status=403)
                
            order.status = "CANCELLED"
            order.save()
            return ok(message="订单已取消")
            
        # Refund logic (Admin Only)
        elif action == "refund":
            if not request.user.is_staff:
                return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone}", status=403)
            
            if order.status != "PAID":
                return error("VALIDATION_ERROR", "当前状态不可退款", status=422)
                
            with transaction.atomic():
                order.status = "REFUNDED"
                order.save()
                
                # Rollback User Membership
                user = order.user
                
                # 1. Deduct days from expiration
                if user.membership_expire_at:
                    user.membership_expire_at -= timedelta(days=order.plan_days)
                
                # 2. Deduct reference values
                # For UPGRADE, this might leave residual discount value in amount, 
                # but reference_days will likely hit 0, preventing future discount abuse.
                user.membership_reference_days = max(0, user.membership_reference_days - order.plan_days)
                user.membership_reference_amount = max(0, user.membership_reference_amount - order.amount)
                
                user.save()
                
            return ok(message="订单已退款，会员权益已扣除")
            
        return error("VALIDATION_ERROR", "未知操作", status=422)
