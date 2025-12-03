import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import HomeView from '../views/HomeView.vue'
import DashboardLayout from '../backviews/layout/DashboardLayout.vue'
import MemberOverview from '../backviews/member/MemberOverview.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/membership',
    name: 'membership',
    component: () => import('../views/VipPurchase.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: DashboardLayout,
    redirect: '/admin/member/overview',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'member/overview',
        name: 'my-member',
        component: MemberOverview,
        meta: { title: '我的会员' }
      },
      {
        path: 'member/orders',
        name: 'my-orders',
        component: () => import('../backviews/member/MyOrders.vue'),
        meta: { title: '我的订单' }
      },
      {
        path: 'member/settings',
        name: 'personal-settings',
        component: () => import('../backviews/member/PersonalSettings.vue'),
        meta: { title: '个人设置' }
      },
      {
        path: 'member/security',
        name: 'account-security',
        component: () => import('../backviews/member/AccountSecurity.vue'),
        meta: { title: '账号安全' }
      },
      // Membership Routes
      {
        path: 'member/plans',
        name: 'admin-plans',
        component: () => import('../backviews/member/MembershipPlans.vue'),
        meta: { title: '会员等级设置', requiresAdmin: true }
      },
      {
        path: 'member/admin-orders',
        name: 'admin-orders',
        component: () => import('../backviews/member/MembershipOrders.vue'),
        meta: { title: '会员订单管理', requiresAdmin: true }
      },
      {
        path: 'member/order-detail',
        name: 'order-detail',
        component: () => import('../backviews/member/OrderDetail.vue'),
        meta: { title: '订单详情' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const token = localStorage.getItem('token')

  // 同步 Store 状态与 LocalStorage
  if (!token && authStore.token) {
    authStore.logout()
  }
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authStore.isLoggedIn) {
      next({ name: 'home' })
    } else {
      // Check for admin requirement
      if (to.matched.some(record => record.meta.requiresAdmin)) {
        if (!authStore.user?.is_staff) {
            next({ name: 'home' }) // Or 403 page
            return
        }
      }
      next()
    }
  } else {
    next()
  }
})

export default router
