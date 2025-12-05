<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { 
    useMessage, NCard, NList, NListItem, NButton, NModal, NForm, NFormItem, NInput, NSpace, NSteps, NStep, NIcon, NInputGroup 
} from 'naive-ui'
import { 
    LockClosedOutline, 
    PhonePortraitOutline, 
    KeyOutline 
} from '@vicons/ionicons5'

const authStore = useAuthStore()
const message = useMessage()

// Phone Change State
const showPhoneModal = ref(false)
const phoneStep = ref(1)
const phoneForm = reactive({
    code: '',
    newPhone: '',
    newCode: ''
})
const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
let timer = null

// Password Change State
const showPasswordModal = ref(false)
const passwordForm = reactive({
    old_password: '',
    new_password: '',
    confirm_password: ''
})

const startCountdown = () => {
    countdown.value = 60
    if (timer) clearInterval(timer)
    timer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
}

onUnmounted(() => {
    if (timer) clearInterval(timer)
})

const sendCode = async (scene, phone) => {
    if (!phone) {
        message.warning('请输入手机号')
        return
    }
    sendingCode.value = true
    try {
        await authStore.sendCode(phone, scene)
        message.success('验证码已发送')
        startCountdown()
    } catch (error) {
        message.error(error.message || '发送失败')
    } finally {
        sendingCode.value = false
    }
}

const handleVerifyOldPhone = async () => {
    if (!phoneForm.code) {
        message.warning('请输入验证码')
        return
    }
    loading.value = true
    try {
        await authStore.verifyOldPhone(phoneForm.code)
        phoneStep.value = 2
        countdown.value = 0
        clearInterval(timer)
    } catch (error) {
        message.error(error.message || '验证失败')
    } finally {
        loading.value = false
    }
}

const handleChangePhone = async () => {
    if (!phoneForm.newPhone || !phoneForm.newCode) {
        message.warning('请填写完整信息')
        return
    }
    loading.value = true
    try {
        await authStore.changeNewPhone(phoneForm.newPhone, phoneForm.newCode)
        message.success('手机号修改成功')
        showPhoneModal.value = false
    } catch (error) {
        message.error(error.message || '修改失败')
    } finally {
        loading.value = false
    }
}

const handleChangePassword = async () => {
    if (!passwordForm.old_password || !passwordForm.new_password || !passwordForm.confirm_password) {
         message.warning('请填写完整信息')
         return
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
        message.error('两次输入的密码不一致')
        return
    }
    loading.value = true
    try {
        await authStore.changePassword(passwordForm)
        message.success('密码修改成功')
        showPasswordModal.value = false
    } catch (error) {
        message.error(error.message || '修改失败')
    } finally {
        loading.value = false
    }
}
</script>

<template>
  <div class="account-security-page">
    <div class="section-title">账号安全</div>
    
    <div class="security-card">
        <div class="security-item">
            <div class="info">
                <div class="label">手机号</div>
                <div class="value">已绑定：{{ authStore.user?.phone }}</div>
            </div>
            <n-button type="primary" color="#18a058" @click="showPhoneModal = true; phoneStep = 1; phoneForm.code=''; phoneForm.newPhone=''; phoneForm.newCode=''">修改手机</n-button>
        </div>
        
        <div class="divider"></div>
        
        <div class="security-item">
            <div class="info">
                <div class="label">登录密码</div>
                <div class="value">定期更换密码可以提高账号安全性</div>
            </div>
            <n-button type="primary" color="#18a058" @click="showPasswordModal = true; passwordForm.old_password=''; passwordForm.new_password=''; passwordForm.confirm_password=''">修改密码</n-button>
        </div>
    </div>

    <div class="bottom-cards">
        <div class="info-card">
            <div class="card-title">隐私政策</div>
            <div class="card-desc">了解我们如何保护您的隐私</div>
        </div>
        <div class="info-card">
            <div class="card-title">用户协议</div>
            <div class="card-desc">查看我们的服务条款和条件</div>
        </div>
    </div>

    <!-- Change Phone Modal -->
    <n-modal v-model:show="showPhoneModal">
        <n-card class="auth-card" :bordered="false" size="large" role="dialog" aria-modal="true" closable @close="showPhoneModal = false">
            <template #header>
                <div class="auth-header">
                    <div class="modal-title">修改手机号</div>
                    <div class="modal-subtitle">为了保障您的账号安全，请验证身份</div>
                </div>
            </template>

            <n-steps :current="phoneStep" status="process" style="margin-bottom: 24px">
                <n-step title="验证身份" />
                <n-step title="绑定新手机" />
            </n-steps>
            
            <div v-if="phoneStep === 1">
                 <div class="phone-display">当前手机号：{{ authStore.user?.phone }}</div>
                 <n-form-item :show-label="false">
                     <n-input-group>
                         <n-input v-model:value="phoneForm.code" placeholder="输入验证码" size="large">
                             <template #prefix><n-icon :component="KeyOutline" /></template>
                         </n-input>
                         <n-button :disabled="countdown > 0 || sendingCode" :loading="sendingCode" @click="sendCode('change_phone_old', authStore.user?.phone)" ghost type="primary" size="large" class="send-code-btn">
                             {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                         </n-button>
                     </n-input-group>
                 </n-form-item>
                 <n-button type="primary" block size="large" @click="handleVerifyOldPhone" :loading="loading" class="submit-btn">下一步</n-button>
            </div>

            <div v-if="phoneStep === 2">
                 <n-form :show-label="false">
                     <n-form-item>
                         <n-input v-model:value="phoneForm.newPhone" placeholder="输入新手机号" size="large">
                             <template #prefix><n-icon :component="PhonePortraitOutline" /></template>
                         </n-input>
                     </n-form-item>
                     <n-form-item>
                         <n-input-group>
                             <n-input v-model:value="phoneForm.newCode" placeholder="输入验证码" size="large">
                                 <template #prefix><n-icon :component="KeyOutline" /></template>
                             </n-input>
                             <n-button :disabled="countdown > 0" @click="sendCode('change_phone_new', phoneForm.newPhone)" ghost type="primary" size="large" class="send-code-btn">
                                 {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
                             </n-button>
                         </n-input-group>
                     </n-form-item>
                     <n-button type="primary" block size="large" @click="handleChangePhone" class="submit-btn">确认修改</n-button>
                 </n-form>
            </div>
        </n-card>
    </n-modal>

    <!-- Change Password Modal -->
    <n-modal v-model:show="showPasswordModal">
        <n-card class="auth-card" :bordered="false" size="large" role="dialog" aria-modal="true" closable @close="showPasswordModal = false">
            <template #header>
                <div class="auth-header">
                    <div class="modal-title">修改密码</div>
                    <div class="modal-subtitle">定期更换密码可以提高账号安全性</div>
                </div>
            </template>
            
            <n-form :model="passwordForm" :show-label="false">
                <n-form-item>
                    <n-input type="password" show-password-on="click" v-model:value="passwordForm.old_password" placeholder="输入旧密码" size="large">
                        <template #prefix><n-icon :component="LockClosedOutline" /></template>
                    </n-input>
                </n-form-item>
                <n-form-item>
                    <n-input type="password" show-password-on="click" v-model:value="passwordForm.new_password" placeholder="输入新密码" size="large">
                        <template #prefix><n-icon :component="LockClosedOutline" /></template>
                    </n-input>
                </n-form-item>
                <n-form-item>
                    <n-input type="password" show-password-on="click" v-model:value="passwordForm.confirm_password" placeholder="再次输入新密码" size="large">
                        <template #prefix><n-icon :component="LockClosedOutline" /></template>
                    </n-input>
                </n-form-item>
                <n-button type="primary" block size="large" @click="handleChangePassword" class="submit-btn">保存</n-button>
            </n-form>
        </n-card>
    </n-modal>
  </div>
</template>

<style scoped>
.account-security-page {
    background-color: #fff;
    padding: 24px;
    border-radius: 8px;
    min-height: calc(100vh - 120px);
}

.section-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 30px;
    color: #333;
    border-left: 4px solid #f0a020;
    padding-left: 12px;
}

.security-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #eee;
    padding: 40px;
    max-width: 700px;
    margin-bottom: 30px;
}

.security-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 10px 0;
}

.divider {
    height: 1px;
    background-color: #f0f0f0;
    margin: 20px 0;
}

.info .label {
    font-weight: bold;
    font-size: 16px;
    color: #333;
    margin-bottom: 8px;
}

.info .value {
    color: #666;
    font-size: 14px;
}

.bottom-cards {
    display: flex;
    gap: 20px;
    max-width: 700px;
}

.info-card {
    flex: 1;
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #eee;
    padding: 24px;
}

.card-title {
    font-weight: bold;
    font-size: 16px;
    color: #333;
    margin-bottom: 12px;
}

.card-desc {
    color: #666;
    font-size: 14px;
}

/* Modal Styles */
.auth-card {
    width: 460px;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.auth-header {
    text-align: center;
}

:deep(.n-card__content) {
    padding-bottom: 32px;
}

.modal-title {
    font-size: 22px;
    color: #333;
    font-weight: 700;
    margin-bottom: 8px;
}

.modal-subtitle {
    font-size: 14px;
    color: #999;
}

.phone-display {
    text-align: center;
    margin-bottom: 20px;
    color: #666;
    font-size: 15px;
    background: #f9f9f9;
    padding: 10px;
    border-radius: 8px;
}

.send-code-btn {
    width: 110px;
}

.submit-btn {
    margin-top: 12px;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 8px;
}

:deep(.n-input .n-input__input-el) {
    height: 40px;
}

:deep(.n-input) {
    border-radius: 8px;
}
</style>
