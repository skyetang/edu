from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import MemberOrder, PaymentTransaction

ORDER_EXPIRATION_MINUTES = 30

def check_and_expire_order(order):
    """
    Check if the order is expired and update status if necessary.
    Returns True if the order was expired during this check, or is already expired.
    Returns False if the order is still valid (PENDING and within time) or in other final states.
    """
    if order.status == "EXPIRED":
        return True
        
    if order.status == "PENDING":
        if timezone.now() > order.created_at + timedelta(minutes=ORDER_EXPIRATION_MINUTES):
            order.status = "EXPIRED"
            order.save()
            return True
            
    return False

@transaction.atomic
def process_payment_success(order, payment_method, external_data=None):
    """
    处理支付成功逻辑：更新订单状态，更新用户会员权益，记录交易流水
    """
    if order.status == "PAID":
        return
        
    # 1. 更新订单
    order.status = "PAID"
    order.payment_method = payment_method
    order.paid_at = timezone.now()
    order.save()

    # 2. 记录交易流水
    if external_data:
        PaymentTransaction.objects.create(
            order=order,
            transaction_type="PAYMENT",
            amount=order.amount,
            platform=payment_method,
            external_transaction_id=external_data.get("trade_no"),
            raw_response=str(external_data),
            status="SUCCESS"
        )
    else:
        # Fallback for mock or missing data
        PaymentTransaction.objects.create(
            order=order,
            transaction_type="PAYMENT",
            amount=order.amount,
            platform=payment_method,
            status="SUCCESS"
        )
    
    # 3. 更新用户会员信息
    user = order.user
    
    # 如果 order.plan 为空（例如套餐被物理删除），尝试使用快照信息恢复逻辑
    # 但为了简单起见，如果套餐被物理删除且没有plan对象，我们假设是异常情况
    # 不过我们在 OrderCreateView 中使用了 MemberOrder.plan 字段，它是 ForeignKey
    # 如果套餐被删除，on_delete=models.SET_NULL，所以 plan 可能为 None
    # 我们这里主要依赖 order.plan_days 和 order.plan_name 等快照字段来计算时间
    # 但是等级 level 依赖于 plan 对象。如果 plan 没了，我们可能无法得知升级后的等级。
    # 不过 OrderCreateView 里面已经写入了逻辑。
    # 我们需要 plan 对象来获取 level。
    
    if not order.plan:
         # 尝试从快照恢复或抛错
         # 这里假设如果不 Upgrade，Level 不变？或者无法处理。
         # 为安全起见，如果 plan 没了，抛出异常或记录日志。
         # 实际上我们应该尽量避免物理删除 Plan。
         if order.order_type in ["NEW", "UPGRADE"]:
             raise ValueError("订单关联套餐已不存在，无法完成权益发放")
    
    if order.order_type == "NEW":
        if order.plan:
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
        if order.plan:
            user.level = order.plan.level
        user.membership_expire_at = timezone.now() + timedelta(days=order.plan_days)
        user.membership_reference_amount = order.amount + order.discount_amount
        user.membership_reference_days = order.plan_days
        
    user.save()
