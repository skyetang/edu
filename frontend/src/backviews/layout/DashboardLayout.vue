<script setup>
import { ref, h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import { 
  NLayout, NLayoutSider, NLayoutHeader, NLayoutContent, NMenu, NDropdown, NAvatar, NIcon, NBreadcrumb, NBreadcrumbItem, NButton, NDrawer, NDrawerContent 
} from 'naive-ui'
import { 
  PersonOutline, 
  DocumentTextOutline, 
  BookOutline, 
  GitNetworkOutline, 
  SettingsOutline,
  LogOutOutline,
  MenuOutline,
  HomeOutline,
  ChevronBack,
  PersonCircleOutline,
  RibbonOutline
} from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth'
import defaultAvatarImg from '@/assets/default.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const message = useMessage()

const collapsed = ref(false)
const showMobileMenu = ref(false)
const isMobile = ref(window.innerWidth <= 768)

// Resize listener
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    showMobileMenu.value = false
  }
})

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = computed(() => {
  const options = [
  {
    label: '会员中心',
    key: 'member-center',
    icon: renderIcon(PersonOutline),
    children: [
      {
        label: '我的会员',
        key: 'my-member'
      },
      {
        label: '我的订单',
        key: 'my-orders'
      }
    ]
  },
  {
    label: '文章管理',
    key: 'articles',
    icon: renderIcon(DocumentTextOutline)
  },
  {
    label: '个人中心',
    key: 'personal-center',
    icon: renderIcon(SettingsOutline),
    children: [
        { label: '个人设置', key: 'personal-settings' },
        { label: '账号安全', key: 'account-security' }
    ]
  }
  ]

  if (authStore.user?.is_staff) {
    // Add Admin Menus
    options.splice(1, 0, {
      label: '会员管理',
      key: 'admin-membership',
      icon: renderIcon(RibbonOutline),
      children: [
        { label: '等级设置', key: 'admin-plans' },
        { label: '订单管理', key: 'admin-orders' }
      ]
    })
    
    options.splice(2, 0, {
      label: '课程管理',
      key: 'courses',
      icon: renderIcon(BookOutline),
      children: [
        { label: '课程管理', key: 'course-list' },
        { label: '分类管理', key: 'course-categories' }
      ]
    })

    options.splice(3, 0, {
      label: '工作流管理',
      key: 'workflows',
      icon: renderIcon(GitNetworkOutline),
      children: [
        { label: '工作流管理', key: 'workflow-list' },
        { label: '分类管理', key: 'workflow-categories' }
      ]
    })
  }

  return options
})

const activeKey = computed(() => {
  return route.name || 'my-member'
})

const breadcrumbList = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched
})

const userOptions = [
  {
    label: '个人中心',
    key: 'personal-center',
    icon: renderIcon(PersonOutline)
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: renderIcon(LogOutOutline)
  }
]

const handleMenuUpdate = (key) => {
  if (key === 'my-member') {
    router.push({ name: 'my-member' })
  } else if (key === 'my-orders') {
    router.push({ name: 'my-orders' })
  } else if (key === 'personal-settings') {
    router.push({ name: 'personal-settings' })
  } else if (key === 'account-security') {
    router.push({ name: 'account-security' })
  } else if (key === 'admin-plans') {
    router.push({ name: 'admin-plans' })
  } else if (key === 'admin-orders') {
    router.push({ name: 'admin-orders' })
  } else if (key === 'course-list') {
    router.push({ name: 'course-list' })
  } else if (key === 'course-categories') {
    router.push({ name: 'course-categories' })
  } else if (key === 'workflow-list') {
    router.push({ name: 'workflow-list' })
  } else if (key === 'workflow-categories') {
    router.push({ name: 'workflow-categories' })
  } else {
    // Placeholder for other routes
    message.info(`Navigating to ${key}`)
  }
  if (isMobile.value) {
    showMobileMenu.value = false
  }
}

const handleUserSelect = (key) => {
  if (key === 'personal-center') {
    router.push({ name: 'personal-settings' })
  } else if (key === 'logout') {
    authStore.logout()
    message.success('已退出登录')
    router.push('/')
  }
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <n-layout class="dashboard-layout" :has-sider="!isMobile">
    <!-- Mobile Header -->
    <n-layout-header v-if="isMobile" class="mobile-header" bordered>
      <div class="mobile-header-left">
        <n-button quaternary circle @click="showMobileMenu = true">
          <template #icon><n-icon><MenuOutline /></n-icon></template>
        </n-button>
        <div class="logo">贝塔AI</div>
      </div>
      <n-dropdown :options="userOptions" @select="handleUserSelect">
        <div class="user-trigger">
          <n-avatar round size="small" :src="authStore.user?.avatar || defaultAvatarImg" />
        </div>
      </n-dropdown>
    </n-layout-header>

    <!-- Desktop Sidebar -->
    <n-layout-sider
      v-if="!isMobile"
      collapse-mode="width"
      :collapsed-width="64"
      :width="200"
      :collapsed="collapsed"
      show-trigger
      @collapse="collapsed = true"
      @expand="collapsed = false"
      class="desktop-sider shadow-sider"
    >
      <div class="sider-logo" :class="{ collapsed }">
        <img src="/vite.svg" alt="Logo" class="logo-img" />
        <span v-if="!collapsed" class="logo-text">贝塔AI</span>
      </div>
      <n-menu
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        :value="activeKey"
        accordion
        @update:value="handleMenuUpdate"
      />
    </n-layout-sider>

    <!-- Mobile Sidebar Drawer -->
    <n-drawer v-model:show="showMobileMenu" placement="left" :width="250">
      <n-drawer-content title="贝塔AI" closable>
        <n-menu
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleMenuUpdate"
        />
      </n-drawer-content>
    </n-drawer>

    <n-layout class="main-layout">
      <!-- Desktop Header -->
      <n-layout-header v-if="!isMobile" class="desktop-header shadow-header">
        <div class="header-left">
          <n-breadcrumb>
            <n-breadcrumb-item>会员中心</n-breadcrumb-item>
            <n-breadcrumb-item>{{ route.meta.title }}</n-breadcrumb-item>
          </n-breadcrumb>
        </div>
        <div class="header-right">
          <n-button text class="home-link" @click="goHome">
            <template #icon><n-icon><HomeOutline /></n-icon></template>
            返回主页
          </n-button>
          <n-dropdown :options="userOptions" @select="handleUserSelect">
            <div class="user-profile">
              <n-avatar round size="medium" :src="authStore.user?.avatar || defaultAvatarImg" />
              <span class="username">{{ authStore.user?.nickname || authStore.user?.phone || '贝塔用户' }}</span>
            </div>
          </n-dropdown>
        </div>
      </n-layout-header>

      <n-layout-content style="background-color: rgb(242, 243, 245);" content-style="padding: 10px; min-height: calc(100vh - 64px);">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.dashboard-layout {
  height: 100vh;
}

.sider-logo {
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  gap: 10px;
}

.logo-img {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  white-space: nowrap;
}

.desktop-header {
  height: 64px;
  padding: 0 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
}

.mobile-header {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
}

.mobile-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-header-left .logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
}

.shadow-sider {
  box-shadow: 2px 0 8px 0 rgb(29 35 41 / 5%);
  z-index: 10;
}

.shadow-header {
  box-shadow: 0 1px 4px rgb(0 21 41 / 8%);
  z-index: 9;
  position: relative;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 40px;
}

.home-link {
  color: #666;
}

.home-link:hover {
  color: var(--primary-color);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.user-profile .username {
  color: #666;
  font-weight: 500;
}
</style>