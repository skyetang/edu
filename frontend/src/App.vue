<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import { NMessageProvider, NConfigProvider, NDialogProvider } from 'naive-ui'
import { themeOverrides } from './theme'

const route = useRoute()
const isBackend = computed(() => route.path.startsWith('/admin'))

// 监听 localStorage 变化，实现多标签页同步登出
window.addEventListener('storage', (e) => {
  if (e.key === 'token' && e.newValue === null) {
    // 如果 token 被清除，且当前在后台管理页面，则刷新页面或跳转
    if (isBackend.value) {
      window.location.href = '/'
    } else {
      // 即使不在后台，也刷新状态
      window.location.reload()
    }
  }
})
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <div class="app-layout">
          <Header v-if="!isBackend" />
          <main class="main-content">
            <router-view />
          </main>
          <Footer v-if="!isBackend" />
        </div>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  background: linear-gradient(135deg, #fff5f0, #fff);
}
</style>
