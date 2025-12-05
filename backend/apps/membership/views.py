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
from .services import check_and_expire_order, process_payment_success
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from decimal import Decimal

User = get_user_model()

class PlanManageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # 管理员查看所有，其他人仅查看已启用
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
            
            # 检查是否存在关联订单
            if MemberOrder.objects.filter(plan=plan).exists():
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
        
        # 使用事务和锁防止竞态条件
        with transaction.atomic():
            # 锁定用户记录以串行化该用户的订单创建
            # 我们使用 select_for_update 锁定用户，确保没有其他事务能同时处理该用户的订单创建
            _lock = User.objects.select_for_update().get(id=user.id)
            
            order_type = "NEW"
            discount_amount = 0
            amount = plan.price
            
            # 确定订单类型
            is_vip = user.membership_expire_at and user.membership_expire_at > timezone.now()
            
            if is_vip:
                if user.level == plan.level:
                    order_type = "RENEWAL"
                elif user.level < plan.level:
                    order_type = "UPGRADE"
                    # 计算升级折扣
                    # 公式：剩余价值 = (参考总价 / 参考总天数) * 剩余天数
                    if user.membership_reference_days > 0:
                        remaining_days = (user.membership_expire_at - timezone.now()).days
                        if remaining_days > 0:
                            daily_rate = Decimal(str(user.membership_reference_amount)) / Decimal(user.membership_reference_days)
                            discount_amount = round(daily_rate * Decimal(remaining_days), 2)
                            
                            # 折扣不能超过套餐价格
                            if discount_amount > plan.price:
                                discount_amount = plan.price
                            
                            amount = plan.price - discount_amount
                else:
                     return error("VALIDATION_ERROR", "不支持降级购买", status=422)
            
            # 检查是否存在待支付订单
            # 1. 查找该用户的所有待支付订单
            pending_orders = MemberOrder.objects.filter(user=user, status="PENDING")
            has_valid_pending_order = False
            
            for pending_order in pending_orders:
                # 2. 检查是否过期（如果超时，此函数将状态更新为已过期）
                is_expired = check_and_expire_order(pending_order)
                if not is_expired:
                    # 如果未过期，说明订单仍然有效且待支付
                    has_valid_pending_order = True
                    break
            
            if has_valid_pending_order:
                return error("VALIDATION_ERROR", "您存在未支付的订单，请先支付或取消后再下单", status=422)

            # 创建待支付订单
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
            
            # 检查并在必要时设置过期
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
        
        # 首先检查过期情况（如果过期则更新状态）
        if check_and_expire_order(order):
            return error("VALIDATION_ERROR", "订单已过期", status=422)
            
        if order.status != "PENDING":
            return error("VALIDATION_ERROR", "订单状态不可支付", status=422)

        # 支付宝支付
        if payment_method == "ALIPAY":
            from .alipay_service import AlipayService
            try:
                result = AlipayService.create_payment_request(order)
                return ok(result)
            except Exception as e:
                # 记录日志并抛出，由全局异常处理或直接返回500
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Alipay creation failed: {e}")
                # 如果是 ValidationException (422) 或 ExternalServiceException (503)，
                # 它们是 APIException 的子类，raise 会被 DRF 捕获并返回对应状态码。
                # 否则如果是普通 Exception，DRF 会返回 500。
                raise

        # 模拟支付流程 (仅用于测试或非支付宝方式)
        try:
            process_payment_success(order, payment_method or "MOCK")
            return ok(message="支付成功，会员已开通")
        except Exception as e:
            return error("SERVER_ERROR", str(e), status=500)

class OrderPaymentQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order_no = request.query_params.get("order_no")
        if not order_no:
            return error("VALIDATION_ERROR", "订单号不能为空", status=422)
        
        try:
            order = MemberOrder.objects.get(order_no=order_no)
            if not request.user.is_staff and order.user != request.user:
                return error("PERMISSION_DENIED", "无权查询此订单", status=403)
        except MemberOrder.DoesNotExist:
            return error("NOT_FOUND", "订单不存在", status=404)

        from .alipay_service import AlipayService
        try:
            result = AlipayService.query_payment_status(order_no)
            return ok(result)
        except Exception as e:
            # 如果查询失败，可能是网络问题，或者支付宝返回错误
            # 我们可以返回当前数据库中的状态
            return ok({
                "order_no": order.order_no,
                "trade_status": "UNKNOWN",
                "local_status": order.status,
                "error": str(e)
            }, message=f"查询支付宝失败，仅返回本地状态")

class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 管理员查看所有，用户查看自己
        scope = request.query_params.get("scope")
        if request.user.is_staff and scope != 'my':
            orders = MemberOrder.objects.all().order_by('-created_at')
        else:
            orders = MemberOrder.objects.filter(user=request.user).order_by('-created_at')
        
        # 分页处理
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # 默认每页10条
        
        # 允许前端控制每页条数
        page_size = request.query_params.get('page_size')
        if page_size:
            paginator.page_size = page_size

        result_page = paginator.paginate_queryset(orders, request)
        serializer = MemberOrderSerializer(result_page, many=True)
        
        # 使用 UnifiedModelViewSet 类似的返回结构
        return ok(data=serializer.data, meta={
            'pagination': {
                'total': paginator.page.paginator.count,
                'page': paginator.page.number,
                'page_size': paginator.page.paginator.per_page
            }
        })

class OrderActionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        order_no = request.data.get("order_no")
        action = request.data.get("action") # cancel, refund
        
        try:
            order = MemberOrder.objects.get(order_no=order_no)
        except MemberOrder.DoesNotExist:
            return error("NOT_FOUND", "订单不存在", status=404)
            
        # 取消逻辑
        if action == "cancel":
            # 首先检查过期情况
            if check_and_expire_order(order):
                return error("VALIDATION_ERROR", "订单已过期，不可取消", status=422)

            if order.status != "PENDING":
                return error("VALIDATION_ERROR", "当前状态不可取消", status=422)
            # 管理员可以取消任何人的订单，用户只能取消自己的
            if not request.user.is_staff and order.user != request.user:
                return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone}", status=403)
                
            order.status = "CANCELLED"
            order.save()
            return ok(message="订单已取消")
            
        # 退款逻辑（仅限管理员）
        elif action == "refund":
            if not request.user.is_staff:
                return error("PERMISSION_DENIED", f"无权操作: User {request.user.phone}", status=403)
            
            # 幂等性检查：如果已经退款，直接返回成功或提示
            if order.status == "REFUNDED":
                return ok(message="订单已经是退款状态")

            if order.status != "PAID":
                return error("VALIDATION_ERROR", "当前状态不可退款", status=422)
                
            # 如果是支付宝支付，先调用支付宝退款
            refund_response = None
            if order.payment_method == "ALIPAY":
                from .alipay_service import AlipayService
                try:
                    refund_response = AlipayService.refund_order(order)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Alipay refund failed: {e}")
                    # 如果退款失败，不继续执行本地回滚
                    return error("SERVER_ERROR", f"支付宝退款失败: {str(e)}", status=500)

            with transaction.atomic():
                order.status = "REFUNDED"
                order.save()

                # 记录退款流水
                from .models import PaymentTransaction
                if refund_response:
                     PaymentTransaction.objects.create(
                        order=order,
                        transaction_type="REFUND",
                        amount=order.amount, # 默认全额退款
                        platform="ALIPAY",
                        external_transaction_id=refund_response.get("trade_no"), # 注意：支付宝退款接口返回的可能不包含 trade_no，而是 out_trade_no (原订单号) 和 refund_fee
                        # 实际上 refund_order 返回的 dict 包含 'refund_fee' 等。支付宝的 trade_no 是原交易号，这里应该尽量记录。
                        # 我们在 refund_order 返回了 'fund_change' 等。
                        # 让我们看看 refund_order 返回了什么: order_no, refund_fee, gmt_refund_pay, fund_change
                        # 它没有返回支付宝的 trade_no (原交易号)，也没有返回本次退款的流水号（支付宝可能不返回新的流水号，而是沿用原 trade_no + out_request_no）
                        # 这里我们简单记录即可。
                        raw_response=str(refund_response),
                        status="SUCCESS"
                    )
                else:
                     # 非支付宝支付的退款（如 Mock 或其他）
                     PaymentTransaction.objects.create(
                        order=order,
                        transaction_type="REFUND",
                        amount=order.amount,
                        platform=order.payment_method or "UNKNOWN",
                        status="SUCCESS"
                    )
                
                # 回滚用户会员信息
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
