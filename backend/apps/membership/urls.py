from django.urls import path
from .views import (
    PlanManageView,
    OrderCreateView,
    OrderDetailView,
    OrderPayView,
    OrderListView,
    OrderActionView,
)

urlpatterns = [
    path('plans/', PlanManageView.as_view(), name='plan-manage'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/detail/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/pay/', OrderPayView.as_view(), name='order-pay'),
    path('orders/list/', OrderListView.as_view(), name='order-list'),
    path('orders/action/', OrderActionView.as_view(), name='order-action'),
]
