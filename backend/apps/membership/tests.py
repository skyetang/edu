from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import MembershipPlan, MemberOrder
from django.utils import timezone
from datetime import timedelta
import time
from decimal import Decimal

User = get_user_model()

class MembershipTests(APITestCase):
    def setUp(self):
        # Create Users
        self.admin = User.objects.create_superuser(
            phone='19999999999',
            password='password123'
        )
        self.user = User.objects.create_user(
            phone='18888888888',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            phone='17777777777',
            password='password123'
        )

        # Create Plans
        self.plan_monthly = MembershipPlan.objects.create(
            name="Monthly Plan",
            price=30.00,
            duration_days=30,
            level=1,
            is_active=True
        )
        self.plan_yearly = MembershipPlan.objects.create(
            name="Yearly Plan",
            price=300.00,
            duration_days=365,
            level=2,
            is_active=True
        )
        self.plan_inactive = MembershipPlan.objects.create(
            name="Old Plan",
            price=10.00,
            duration_days=7,
            level=1,
            is_active=False
        )

    def authenticate_user(self):
        self.client.force_authenticate(user=self.user)

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)

    # --- Plan Management Tests ---

    def test_get_plans_anonymous(self):
        response = self.client.get('/api/membership/plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2) # Only active plans

    def test_get_plans_admin(self):
        self.authenticate_admin()
        response = self.client.get('/api/membership/plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 3) # All plans

    def test_create_plan_admin(self):
        self.authenticate_admin()
        data = {
            "name": "New Plan",
            "price": 50.00,
            "duration_days": 60,
            "level": 1,
            "description": "Test"
        }
        response = self.client.post('/api/membership/plans/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(MembershipPlan.objects.filter(name="New Plan").exists())

    def test_create_plan_user_denied(self):
        self.authenticate_user()
        response = self.client.post('/api/membership/plans/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_plan_physical(self):
        """Test physical deletion when no orders exist"""
        self.authenticate_admin()
        # Create a temp plan
        plan = MembershipPlan.objects.create(name="Temp", price=1, duration_days=1, level=1)
        response = self.client.delete(f'/api/membership/plans/?id={plan.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(MembershipPlan.objects.filter(id=plan.id).exists())

    def test_delete_plan_soft(self):
        """Test soft deletion when orders exist"""
        self.authenticate_admin()
        # Create order for plan_monthly
        MemberOrder.objects.create(
            order_no="TEST001",
            user=self.user,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PAID"
        )
        
        response = self.client.delete(f'/api/membership/plans/?id={self.plan_monthly.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Plan should still exist but be inactive
        self.plan_monthly.refresh_from_db()
        self.assertTrue(MembershipPlan.objects.filter(id=self.plan_monthly.id).exists())
        self.assertFalse(self.plan_monthly.is_active)
        self.assertIn("下架", response.data['message'])

    # --- Order Creation Tests ---

    def test_create_order_success(self):
        self.authenticate_user()
        data = {"plan_id": self.plan_monthly.id}
        response = self.client.post('/api/membership/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'PENDING')
        self.assertEqual(float(response.data['data']['amount']), 30.00)

    def test_create_order_pending_exists(self):
        self.authenticate_user()
        # Create a pending order first
        MemberOrder.objects.create(
            order_no="PENDING001",
            user=self.user,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PENDING",
            created_at=timezone.now()
        )
        
        # Try to create another
        data = {"plan_id": self.plan_monthly.id}
        response = self.client.post('/api/membership/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("存在未支付的订单", response.data['message'])

    def test_create_order_pending_expired(self):
        self.authenticate_user()
        # Create an expired pending order (older than 30 mins)
        expired_time = timezone.now() - timedelta(minutes=31)
        order = MemberOrder.objects.create(
            order_no="EXPIRED001",
            user=self.user,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PENDING"
        )
        # Mock creation time manually since auto_now_add might override
        MemberOrder.objects.filter(id=order.id).update(created_at=expired_time)
        
        # Try to create another - should succeed as old one expires
        data = {"plan_id": self.plan_monthly.id}
        response = self.client.post('/api/membership/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check old order status
        order.refresh_from_db()
        self.assertEqual(order.status, 'EXPIRED')

    def test_upgrade_order_calculation(self):
        self.authenticate_user()
        # Setup user as Monthly VIP
        self.user.level = 1
        self.user.membership_expire_at = timezone.now() + timedelta(days=15) # 15 days left
        self.user.membership_reference_amount = Decimal('30.00')
        self.user.membership_reference_days = 30
        self.user.save()
        
        # Buy Yearly (Level 2)
        data = {"plan_id": self.plan_yearly.id}
        response = self.client.post('/api/membership/orders/create/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Calculate expected discount
        # Daily rate = 30 / 30 = 1.0
        # Remaining value = 1.0 * 15 = 15.0
        # Expected price = 300 - 15 = 285.0
        self.assertEqual(response.data['data']['order_type'], 'UPGRADE')
        self.assertEqual(float(response.data['data']['discount_amount']), 15.00)
        self.assertEqual(float(response.data['data']['amount']), 285.00)

    # --- Payment Tests ---

    def test_pay_order_success(self):
        self.authenticate_user()
        # Create Pending Order
        response_create = self.client.post('/api/membership/orders/create/', {"plan_id": self.plan_monthly.id})
        order_no = response_create.data['data']['order_no']
        
        # Pay
        data = {"order_no": order_no, "payment_method": "ALIPAY"}
        response = self.client.post('/api/membership/orders/pay/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check Order Status
        order = MemberOrder.objects.get(order_no=order_no)
        self.assertEqual(order.status, 'PAID')
        
        # Check User Status
        self.user.refresh_from_db()
        self.assertEqual(self.user.level, 1)
        self.assertIsNotNone(self.user.membership_expire_at)
        self.assertTrue(self.user.membership_expire_at > timezone.now() + timedelta(days=29))

    def test_pay_others_order_fail(self):
        self.authenticate_user()
        # User2 creates order
        order = MemberOrder.objects.create(
            order_no="USER2_ORDER",
            user=self.user2,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PENDING"
        )
        
        # User1 tries to pay
        data = {"order_no": "USER2_ORDER", "payment_method": "ALIPAY"}
        response = self.client.post('/api/membership/orders/pay/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Action Tests ---

    def test_cancel_order(self):
        self.authenticate_user()
        order = MemberOrder.objects.create(
            order_no="CANCEL_TEST",
            user=self.user,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PENDING"
        )
        
        response = self.client.post('/api/membership/orders/action/', {
            "order_no": "CANCEL_TEST",
            "action": "cancel"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, "CANCELLED")

    def test_refund_order_admin(self):
        self.authenticate_admin()
        # Setup user with paid order and active membership
        order = MemberOrder.objects.create(
            order_no="REFUND_TEST",
            user=self.user,
            plan=self.plan_monthly,
            plan_name=self.plan_monthly.name,
            plan_days=self.plan_monthly.duration_days,
            amount=30.00,
            status="PAID",
            paid_at=timezone.now()
        )
        self.user.level = 1
        self.user.membership_expire_at = timezone.now() + timedelta(days=30)
        self.user.membership_reference_amount = 30.00
        self.user.membership_reference_days = 30
        self.user.save()
        
        response = self.client.post('/api/membership/orders/action/', {
            "order_no": "REFUND_TEST",
            "action": "refund"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check Order
        order.refresh_from_db()
        self.assertEqual(order.status, "REFUNDED")
        
        # Check User Rollback (Should reduce days)
        self.user.refresh_from_db()
        # Expiration should be back to near now (since we added 30 days then removed 30 days)
        # Allow small delta for execution time
        time_diff = abs((self.user.membership_expire_at - timezone.now()).total_seconds())
        self.assertTrue(time_diff < 60) 
