<script setup>
import { ref, computed, watch } from 'vue'
import { 
  NModal, NCard, NTabs, NTabPane, NForm, NFormItem, NInput, NButton, NInputGroup, NCheckbox, useMessage, NIcon
} from 'naive-ui'
import { 
  LockClosedOutline, 
  KeyOutline, 
  PhonePortraitOutline 
} from '@vicons/ionicons5'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['update:show', 'success'])

const authStore = useAuthStore()
const message = useMessage()

const activeTab = ref('login')
const loginMethod = ref('password')

// Reset state when modal opens
watch(() => props.show, (newVal) => {
  if (newVal) {
    activeTab.value = 'login'
    loginMethod.value = 'password'
    // Clear forms if needed
    loginCodeForm.value = { phone: '', code: '' }
    loginPasswordForm.value = { phone: '', password: '' }
    registerForm.value = { phone: '', password: '', confirmPassword: '', code: '', agree: false }
  }
})

const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let timer = null

// Login Form (SMS Code Only)
const loginCodeForm = ref({
  phone: '',
  code: ''
})

// Login Form (Password)
const loginPasswordForm = ref({
  phone: '',
  password: ''
})

// Register Form
const registerForm = ref({
  phone: '',
  password: '',
  confirmPassword: '',
  code: '',
  agree: false
})

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, max: 6, message: '验证码为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value) => value === registerForm.value.password,
      message: '两次输入的密码不一致',
      trigger: 'blur'
    }
  ]
}

const currentPhone = computed(() => activeTab.value === 'login' ? loginCodeForm.value.phone : registerForm.value.phone)

const startCountdown = () => {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const handleSendCode = async () => {
  const phone = currentPhone.value
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    message.error('请输入正确的手机号')
    return
  }
  sendingCode.value = true
  try {
    const scene = activeTab.value === 'register' ? 'register' : 'login'
    await authStore.sendCode(phone, scene)
    message.success('验证码已发送')
    startCountdown()
  } catch (err) {
    if (!err.isGloballyHandled) {
        message.error(err.message || '发送失败')
    }
  } finally {
    sendingCode.value = false
  }
}

const handleSubmitLogin = async () => {
  loading.value = true
  try {
    if (loginMethod.value === 'password') {
      await authStore.loginWithPassword(loginPasswordForm.value.phone, loginPasswordForm.value.password)
    } else {
      await authStore.loginWithCode(loginCodeForm.value.phone, loginCodeForm.value.code)
    }
    message.success('登录成功')
    emit('update:show', false)
    emit('success')
  } catch (err) {
    if (!err.isGloballyHandled) {
        message.error(err.message || '登录失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmitRegister = async () => {
  if (!registerForm.value.agree) {
    message.error('请阅读并同意相关协议')
    return
  }
  loading.value = true
  try {
    await authStore.register(
      registerForm.value.phone,
      registerForm.value.code,
      registerForm.value.password
    )
    message.success('注册成功')
    activeTab.value = 'login'
  } catch (err) {
    if (!err.isGloballyHandled) {
        message.error(err.message || '注册失败')
    }
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="show" @update:show="emit('update:show', $event)">
    <n-card
      class="auth-card"
      :bordered="false"
      size="large"
      role="dialog"
      aria-modal="true"
      closable
      @close="handleClose"
    >
      <template #header>
        <div class="auth-header">
          <div class="modal-title">{{ activeTab === 'login' ? '欢迎登录' : '注册账号' }}</div>
          <div class="modal-subtitle">加入贝塔AI，开启学习之旅</div>
        </div>
      </template>

      <div v-if="activeTab === 'login'" class="auth-body">
        <n-tabs 
          v-model:value="loginMethod" 
          type="segment" 
          animated 
          class="auth-tabs"
        >
          <n-tab-pane name="password" tab="密码登录">
            <n-form :model="loginPasswordForm" :rules="rules" :show-label="false" class="auth-form">
              <n-form-item path="phone">
                <n-input 
                  v-model:value="loginPasswordForm.phone" 
                  placeholder="请输入手机号" 
                  size="large"
                >
                  <template #prefix>
                    <n-icon :component="PhonePortraitOutline" />
                  </template>
                </n-input>
              </n-form-item>
              <n-form-item path="password">
                <n-input 
                  v-model:value="loginPasswordForm.password" 
                  type="password" 
                  show-password-on="click" 
                  placeholder="请输入密码" 
                  size="large"
                  @keyup.enter="handleSubmitLogin"
                >
                  <template #prefix>
                    <n-icon :component="LockClosedOutline" />
                  </template>
                </n-input>
              </n-form-item>
              <n-button 
                type="primary" 
                block 
                size="large" 
                class="submit-btn" 
                @click="handleSubmitLogin" 
                :loading="loading"
              >
                立即登录
              </n-button>
            </n-form>
          </n-tab-pane>
          
          <n-tab-pane name="code" tab="验证码登录">
            <n-form :model="loginCodeForm" :rules="rules" :show-label="false" class="auth-form">
              <n-form-item path="phone">
                <n-input 
                  v-model:value="loginCodeForm.phone" 
                  placeholder="请输入手机号" 
                  size="large"
                >
                  <template #prefix>
                    <n-icon :component="PhonePortraitOutline" />
                  </template>
                </n-input>
              </n-form-item>
              <n-form-item path="code">
                <n-input-group>
                  <n-input 
                    v-model:value="loginCodeForm.code" 
                    placeholder="请输入验证码" 
                    size="large"
                    @keyup.enter="handleSubmitLogin"
                  >
                    <template #prefix>
                      <n-icon :component="KeyOutline" />
                    </template>
                  </n-input>
                  <n-button 
                    :disabled="countdown > 0 || sendingCode"
                    :loading="sendingCode" 
                    @click="handleSendCode" 
                    ghost
                    type="primary" 
                    size="large"
                    class="send-code-btn"
                  >
                    {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                  </n-button>
                </n-input-group>
              </n-form-item>
              <n-button 
                type="primary" 
                block 
                size="large" 
                class="submit-btn" 
                @click="handleSubmitLogin" 
                :loading="loading"
              >
                立即登录
              </n-button>
            </n-form>
          </n-tab-pane>
        </n-tabs>
        
        <div class="auth-footer">
          还没有账号？ <span class="link" @click="activeTab = 'register'">立即注册</span>
        </div>
      </div>

      <div v-if="activeTab === 'register'" class="auth-body">
        <n-form :model="registerForm" :rules="rules" :show-label="false" class="auth-form">
          <n-form-item path="phone">
            <n-input 
              v-model:value="registerForm.phone" 
              placeholder="请输入手机号" 
              size="large"
            >
              <template #prefix>
                <n-icon :component="PhonePortraitOutline" />
              </template>
            </n-input>
          </n-form-item>
          <n-form-item path="password">
            <n-input 
              v-model:value="registerForm.password" 
              type="password" 
              show-password-on="click" 
              placeholder="设置密码（6位以上）" 
              size="large"
            >
              <template #prefix>
                <n-icon :component="LockClosedOutline" />
              </template>
            </n-input>
          </n-form-item>
          <n-form-item path="confirmPassword">
            <n-input 
              v-model:value="registerForm.confirmPassword" 
              type="password" 
              show-password-on="click" 
              placeholder="确认密码" 
              size="large"
              @keyup.enter="handleSubmitRegister"
            >
              <template #prefix>
                <n-icon :component="LockClosedOutline" />
              </template>
            </n-input>
          </n-form-item>
          <n-form-item path="code">
            <n-input-group>
              <n-input 
                v-model:value="registerForm.code" 
                placeholder="请输入验证码" 
                size="large"
              >
                <template #prefix>
                  <n-icon :component="KeyOutline" />
                </template>
              </n-input>
              <n-button 
                :disabled="countdown > 0 || sendingCode" 
                :loading="sendingCode"
                @click="handleSendCode" 
                ghost
                type="primary" 
                size="large"
                class="send-code-btn"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </n-button>
            </n-input-group>
          </n-form-item>

          <div class="agreements">
            <n-checkbox v-model:checked="registerForm.agree">
              我已阅读并同意 <span class="link">《用户协议》</span> 和 <span class="link">《隐私协议》</span>
            </n-checkbox>
          </div>

          <n-button 
            type="primary" 
            block 
            size="large" 
            class="submit-btn" 
            @click="handleSubmitRegister" 
            :loading="loading"
          >
            立即注册
          </n-button>
          
          <div class="auth-footer">
            已有账号？ <span class="link" @click="activeTab = 'login'">去登录</span>
          </div>
        </n-form>
      </div>
    </n-card>
  </n-modal>
</template>

<style scoped>
.auth-card {
  width: 400px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-top: 0;
}

.logo-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 107, 53, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.modal-title {
  font-size: 24px;
  color: #333;
  font-weight: 700;
  margin-bottom: 8px;
}

.modal-subtitle {
  font-size: 14px;
  color: #999;
}

.auth-tabs {
  margin-bottom: 24px;
}

.auth-form {
  margin-top: 16px;
}

.submit-btn {
  margin-top: 12px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.send-code-btn {
  width: 110px;
}

.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.link {
  color: var(--primary-color);
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
}

.link:hover {
  opacity: 0.8;
}

.agreements {
  margin: 12px 0 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
}

:deep(.n-card__content) {
  padding: 0 32px 58px;
}

:deep(.n-input .n-input__input-el) {
  height: 40px;
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-tabs-nav--segment-type .n-tabs-nav-scroll-content) {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 4px;
}

:deep(.n-tabs .n-tabs-tab.n-tabs-tab--active) {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  font-weight: 600;
  color: var(--primary-color);
}
</style>
