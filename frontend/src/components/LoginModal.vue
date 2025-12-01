<script setup>
import { ref, computed } from 'vue'
import { 
  NModal, NCard, NTabs, NTabPane, NForm, NFormItem, NInput, NButton, NInputGroup, NCheckbox, useMessage 
} from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['update:show', 'success'])

const authStore = useAuthStore()
const message = useMessage()

const activeTab = ref('login')
const loginMethod = ref('password')
const loading = ref(false)
const countdown = ref(0)
let timer = null

// Login Form (SMS Code Only)
const loginCodeForm = ref({
  phone: '',
  code: ''
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
  try {
    const scene = activeTab.value === 'register' ? 'register' : 'login'
    await authStore.sendCode(phone, scene)
    message.success('验证码已发送')
    startCountdown()
  } catch (err) {
    message.error(err.message || '发送失败')
  }
}

const handleSubmitLogin = async () => {
  loading.value = true
  try {
    await authStore.loginWithCode(loginCodeForm.value.phone, loginCodeForm.value.code)
    message.success('登录成功')
    emit('update:show', false)
    emit('success')
  } catch (err) {
    message.error(err.message || '登录失败')
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
    message.error(err.message || '注册失败')
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
      style="width: 420px"
      :bordered="false"
      size="huge"
      role="dialog"
      aria-modal="true"
      closable
      @close="handleClose"
    >
      <div class="modal-title">{{ activeTab === 'login' ? '用户登录' : '用户注册' }}</div>
      <div v-if="activeTab === 'login'" class="login-block">
        <n-tabs v-model:value="loginMethod" type="line" justify-content="flex-start" class="login-tabs">
          <n-tab-pane name="password" tab="密码登录">
            <n-form :model="loginPasswordForm" :rules="rules" class="form-block compact" label-placement="left" label-width="80">
              <n-form-item path="phone" label="手机号">
                <n-input v-model:value="loginPasswordForm.phone" placeholder="请输入手机号" />
              </n-form-item>
              <n-form-item path="password" label="密码">
                <n-input v-model:value="loginPasswordForm.password" type="password" show-password-on="click" placeholder="请输入密码" />
              </n-form-item>
              <n-button type="primary" block size="large" class="primary-action" @click="handleSubmitLogin" :loading="loading">登录</n-button>
              <div class="switch-tip">还没有账号？ <a class="link" @click="activeTab = 'register'">点击注册</a></div>
            </n-form>
          </n-tab-pane>
          <n-tab-pane name="code" tab="验证码登录">
            <n-form :model="loginCodeForm" :rules="rules" class="form-block compact" label-placement="left" label-width="80">
              <n-form-item path="phone" label="手机号">
                <n-input v-model:value="loginCodeForm.phone" placeholder="请输入手机号" />
              </n-form-item>
              <n-form-item path="code" label="验证码">
                <n-input-group>
                  <n-input v-model:value="loginCodeForm.code" placeholder="请输入验证码" />
                  <n-button :disabled="countdown > 0" @click="handleSendCode" type="primary" class="send-code">
                    {{ countdown > 0 ? `${countdown}s后重发` : '发送验证码' }}
                  </n-button>
                </n-input-group>
              </n-form-item>
              <n-button type="primary" block size="large" class="primary-action" @click="handleSubmitLogin" :loading="loading">登录</n-button>
              <div class="switch-tip">还没有账号？ <a class="link" @click="activeTab = 'register'">点击注册</a></div>
            </n-form>
          </n-tab-pane>
        </n-tabs>
      </div>

      <div v-if="activeTab === 'register'" class="register-block">
        <n-form :model="registerForm" :rules="rules" class="form-block" label-placement="left" label-width="80">
          <n-form-item path="phone" label="手机号">
            <n-input v-model:value="registerForm.phone" placeholder="请输入手机号" />
          </n-form-item>
          <n-form-item path="password" label="密码">
            <n-input v-model:value="registerForm.password" type="password" show-password-on="click" placeholder="请输入密码" />
          </n-form-item>
          <n-form-item path="confirmPassword" label="确认密码">
            <n-input v-model:value="registerForm.confirmPassword" type="password" show-password-on="click" placeholder="请再次输入密码" />
          </n-form-item>
          <n-form-item path="code" label="验证码">
            <n-input-group>
              <n-input v-model:value="registerForm.code" placeholder="请输入验证码" />
              <n-button :disabled="countdown > 0" @click="handleSendCode" type="primary" class="send-code">{{ countdown > 0 ? `${countdown}s后重发` : '发送验证码' }}</n-button>
            </n-input-group>
          </n-form-item>

          <div class="agreements">
            <n-checkbox v-model:checked="registerForm.agree">我已阅读并同意 <a class="link">《用户协议》</a> <a class="link">《隐私协议》</a></n-checkbox>
          </div>

          <n-button type="primary" block size="large" class="primary-action" @click="handleSubmitRegister" :loading="loading">注册</n-button>
          <div class="switch-tip">已有账号，<a class="link" @click="activeTab = 'login'">点击登录</a></div>
        </n-form>
      </div>
    </n-card>
  </n-modal>
</template>

<style scoped>
.modal-title {
  text-align: center;
  font-size: 22px;
  color: var(--primary-color);
  font-weight: 700;
  margin-bottom: 8px;
}

.login-block { margin-top: 8px; }

.form-block :deep(.n-form-item-label) {
  color: #333;
  font-weight: 500;
}
.req { color: #ff4d4f; margin-left: 4px; }

.send-code {
  margin-left: 8px;
}

.primary-action {
  margin-top: 6px;
  border-radius: 10px;
  background: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(25, 190, 107, 0.4) inset;
}

.switch-tip {
  margin-top: 8px;
  text-align: center;
  color: #666;
}
.link { color: var(--primary-color); cursor: pointer; }

.agreements {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}
</style>
