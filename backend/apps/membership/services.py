from django.utils import timezone
from datetime import timedelta

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
