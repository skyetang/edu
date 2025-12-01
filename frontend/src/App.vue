<script setup>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'
import { NMessageProvider } from 'naive-ui'
</script>

<template>
  <n-message-provider>
    <div class="app-layout">
      <Header />
      <main class="main-content">
        <router-view />
      </main>
      <Footer />
    </div>
  </n-message-provider>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}
</style>
