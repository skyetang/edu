<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginModal from './LoginModal.vue'
import { NButton, NDropdown, NAvatar } from 'naive-ui'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)
const showLoginModal = ref(false)

const menuItems = [
  { label: '首页', key: 'home', path: '/' },
  { label: '视频课程', key: 'courses', path: '/courses' },
  { label: '工作流案例', key: 'cases', path: '/cases' },
  { label: 'VIP会员', key: 'membership', path: '/membership' },
  { label: '技术文档', key: 'docs', path: '/docs' },
]

const userOptions = [
  { label: '个人中心', key: 'profile' },
  { label: '退出登录', key: 'logout' }
]

const handleUserSelect = (key) => {
  if (key === 'logout') {
    authStore.logout()
    router.push('/')
  } else if (key === 'profile') {
    router.push('/profile') // Assuming profile page exists or will exist
  }
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const navigateTo = (path) => {
  router.push(path)
  mobileMenuOpen.value = false
}

const handleLoginClick = () => {
  showLoginModal.value = true
}
</script>

<template>
  <header class="header">
    <div class="container header-content">
      <!-- Logo -->
      <div class="logo" @click="navigateTo('/')">
        <img src="/vite.svg" alt="Logo" class="logo-img" /> <!-- Placeholder logo -->
        <span class="logo-text">贝塔AI</span>
      </div>

      <!-- Desktop Navigation -->
      <nav class="desktop-nav">
        <a 
          v-for="item in menuItems" 
          :key="item.key" 
          @click.prevent="navigateTo(item.path)"
          class="nav-link"
          :class="{ active: router.currentRoute.value.path === item.path }"
        >
          {{ item.label }}
        </a>
      </nav>

      <!-- Auth Buttons -->
      <div class="auth-buttons desktop-auth">
        <div v-if="authStore.isLoggedIn" class="user-info">
          <n-dropdown trigger="hover" :options="userOptions" @select="handleUserSelect">
            <div class="user-trigger" @click="navigateTo('/profile')">
              <span class="user-name">{{ authStore.user?.phone || '用户' }}</span>
            </div>
          </n-dropdown>
        </div>
        <n-button 
          v-else 
          type="primary" 
          class="login-btn" 
          @click="handleLoginClick"
        >
          登录
        </n-button>
      </div>

      <!-- Mobile Menu Toggle -->
      <div class="mobile-toggle" @click="toggleMobileMenu">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    </div>

    <!-- Mobile Navigation Drawer -->
    <div class="mobile-menu" :class="{ open: mobileMenuOpen }">
      <nav class="mobile-nav-links">
        <a 
          v-for="item in menuItems" 
          :key="item.key" 
          @click.prevent="navigateTo(item.path)"
          class="mobile-nav-link"
        >
          {{ item.label }}
        </a>
        <div class="mobile-auth">
          <div v-if="authStore.isLoggedIn" class="mobile-user">
             <span class="mobile-user-name">{{ authStore.user?.phone }}</span>
             <n-button size="small" @click="authStore.logout()">退出</n-button>
          </div>
          <n-button v-else type="primary" block @click="handleLoginClick">登录 / 注册</n-button>
        </div>
      </nav>
    </div>

    <LoginModal v-model:show="showLoginModal" />
  </header>
</template>

<style scoped>
.header {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
  font-size: 22px;
  color: var(--primary-color);
  margin-right: 40px;
}

.logo-img {
  height: 28px;
  margin-right: 10px;
}

.logo-text {
  color: var(--primary-color);
}

.desktop-nav {
  display: flex;
  gap: 30px;
  margin-left: auto; /* Push to right */
  margin-right: 30px;
}

.nav-link {
  font-size: 14px;
  color: #333; /* Darker text color requested */
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
  position: relative;
}

.nav-link:hover, .nav-link.active {
  color: var(--primary-color);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--primary-color);
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 15px;
}

.login-btn {
  padding: 0 20px;
  font-weight: 500;
}

.user-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
  font-size: 14px;
}

.user-trigger:hover {
  color: var(--primary-color);
}

.mobile-toggle {
  display: none;
  flex-direction: column;
  gap: 5px;
  cursor: pointer;
  margin-left: auto;
}

.bar {
  width: 25px;
  height: 3px;
  background-color: #333;
  transition: 0.3s;
}

/* Mobile Menu Styles */
.mobile-menu {
  position: absolute;
  top: 60px;
  left: 0;
  width: 100%;
  background-color: #fff;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transform: translateY(-150%);
  transition: transform 0.3s ease;
  z-index: 99;
}

.mobile-menu.open {
  transform: translateY(0);
}

.mobile-nav-links {
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.mobile-nav-link {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 16px;
  color: #333;
}

.mobile-auth {
  margin-top: 20px;
}

.mobile-user {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .desktop-nav, .desktop-auth {
    display: none;
  }

  .mobile-toggle {
    display: flex;
  }
}
</style>
