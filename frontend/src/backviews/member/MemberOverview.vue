<template>
  <div class="member-overview">
    <div class="section-title">会员信息</div>
    
    <div class="member-card-wrapper">
      <div class="member-card" :class="{ 'not-vip': !isVip }">
        <div class="card-content">
          <div class="user-info">
            <img v-if="authStore.user?.avatar" :src="authStore.user?.avatar" class="avatar" alt="avatar" />
            <img v-else :src="defaultAvatarImg" class="avatar" alt="default avatar" />
            <div class="info-text">
              <div class="welcome">欢迎回来：{{ authStore.user?.nickname || authStore.user?.phone || '贝塔AI用户' }}</div>
              <div class="tags">
                <span class="vip-tag" v-if="isVip || isAdmin">
                  <span class="crown" v-if="!isAdmin">👑</span> {{ userLevelDisplay }}
                </span>
                <span class="vip-tag gray" v-else>普通用户</span>
              </div>
            </div>
          </div>
          
          <div class="validity-info" v-if="isVip">
            <div class="validity-item">
              <div class="label">会员有效期至</div>
              <div class="value date-value">{{ formatDateTime(expireDate) }}</div>
            </div>
            <div class="validity-divider"></div>
            <div class="validity-item right-align">
              <div class="label">剩余天数</div>
              <div class="value day-value">
                {{ remainingDays }}<span class="unit">天</span>
              </div>
            </div>
          </div>
          <div class="validity-info empty-state" v-else>
             <div class="validity-item">
              <div class="label">您当前还不是会员</div>
              <div class="value text-value">开通会员享受更多权益</div>
            </div>
          </div>
          
          <div class="action-area">
            <n-button class="renew-btn" @click="handleRenew" :class="{ 'is-vip-btn': isVip }">
              {{ isVip ? '立即续费' : '立即开通' }}
            </n-button>
          </div>
        </div>
      </div>
    </div>

    <div class="section-divider"></div>

    <div class="section-title contact-title">联系我们</div>
    
    <div class="contact-steps">
      <div class="step-item">
        <div class="step-icon">1</div>
        <div class="step-content">
          <div class="step-text">请添加站长微信，点击放大(截图扫码)</div>
          <div class="qr-placeholder">
            <!-- 这里应该替换为真实的二维码图片 -->
            <img :src="qrCodeImg" alt="QR Code" class="qr-code" />
          </div>
        </div>
      </div>
      
      <div class="step-item">
        <div class="step-icon">2</div>
        <div class="step-content">
          <div class="step-text">说明需要咨询内容或问题</div>
        </div>
      </div>
      
      <div class="step-item">
        <div class="step-icon">3</div>
        <div class="step-content">
          <div class="step-text">发送您当前账号绑定的手机号</div>
        </div>
      </div>
      
      <div class="step-item">
        <div class="step-icon">4</div>
        <div class="step-content">
          <div class="step-text">处理与解决</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NButton, NIcon } from 'naive-ui'
import { PersonCircleOutline } from '@vicons/ionicons5'
import { useAuthStore } from '../../stores/auth'
import qrCodeImg from '@/assets/qrcode.png'
import defaultAvatarImg from '@/assets/default.png'

const authStore = useAuthStore()
const router = useRouter()

const expireDate = computed(() => {
  return authStore.user?.membership_expire_at
})

const isVip = computed(() => {
  if (!expireDate.value) return false
  return new Date(expireDate.value) > new Date()
})

const isAdmin = computed(() => {
  const user = authStore.user
  return user && (user.is_staff || user.is_superuser)
})

const userLevelDisplay = computed(() => {
  if (isAdmin.value) return '管理员'
  if (isVip.value) return authStore.user?.level_display || 'VIP会员'
  return '普通用户'
})

const remainingDays = computed(() => {
  if (!isVip.value) return 0
  const end = new Date(expireDate.value)
  const now = new Date()
  const diff = end - now
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const handleRenew = () => {
  router.push({ name: 'membership' })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
</script>

<style scoped>
.member-overview {
  max-width: 100%;
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  min-height: calc(100vh - 120px);
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
  border-left: 4px solid #ff6b35;
  padding-left: 12px;
  line-height: 1.2;
}

.section-divider {
  height: 1px;
  background-color: #eee;
  margin: 40px 0;
}

.contact-title {
  margin-top: 0;
}

.member-card-wrapper {
  max-width: 680px;
  margin: 0;
}

.member-card {
  /* Premium Gradient for VIP */
  background: linear-gradient(135deg, rgb(255, 167, 106), rgb(255, 118, 118));
  border-radius: 10px;
  padding: 24px;
  color: #fff;
  box-shadow: 0 12px 30px rgba(255, 118, 118, 0.3);
  position: relative;
  overflow: hidden;
  border: none;
}

.member-card.not-vip {
  /* Soft Silver/Grey Gradient for Non-VIP */
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  color: #333;
  border: 1px solid #e0e0e0;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.member-card::before {
  /* Subtle texture overlay */
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
  pointer-events: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.2);
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.not-vip .avatar {
  border-color: #fff;
}

.info-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.welcome {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.not-vip .welcome {
  color: #2c3e50;
}

.tags {
  display: flex;
}

.vip-tag {
  background: linear-gradient(90deg, #FFD700 0%, #FDB931 100%);
  color: #5a3a00;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
}

.vip-tag::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
  animation: shine 6s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  20% { left: 200%; }
  100% { left: 200%; }
}

.vip-tag.gray {
  background: #e0e0e0;
  color: #666;
  box-shadow: none;
}

.validity-info {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 18px 26px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  position: relative;
  z-index: 1;
  min-height: 110px;
}

.member-card.not-vip .validity-info {
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.validity-divider {
  width: 1px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 24px;
}

.member-card.not-vip .validity-divider {
  background: rgba(0, 0, 0, 0.1);
}

.validity-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.validity-item.right-align {
  align-items: flex-end;
}

.validity-item .label {
  font-size: 13px;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.member-card.not-vip .validity-item .label {
  color: #666;
  opacity: 1;
}

.validity-item .value {
  font-weight: 500;
  line-height: 1.1;
}

.date-value {
  font-size: 28px;
  font-family: 'Monaco', 'Consolas', monospace; /* Tech/Premium feel for dates */
  letter-spacing: -0.5px;
}

.day-value {
  font-size: 42px;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.member-card.not-vip .date-value, 
.member-card.not-vip .day-value {
  color: #333;
  text-shadow: none;
}

.text-value {
  font-size: 20px;
  font-weight: 600;
}

.unit {
  font-size: 14px;
  margin-left: 4px;
  font-weight: 500;
  opacity: 0.8;
  color: #f0e6d2;
}

.member-card.not-vip .unit {
  color: #666;
}

.action-area {
  display: flex;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.renew-btn {
  width: 200px;
  height: 50px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
  border: none;
  transition: all 0.3s ease;
  background: #333; /* Default for non-VIP */
  color: #fff;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.renew-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: #444;
}

.renew-btn.is-vip-btn {
  background: linear-gradient(90deg, #FFD700 0%, #FDB931 100%);
  color: #5a3a00;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.renew-btn.is-vip-btn:hover {
  background: linear-gradient(90deg, #ffe033 0%, #ffc44d 100%);
  box-shadow: 0 6px 25px rgba(255, 215, 0, 0.4);
}

/* Contact Section */
.contact-steps {
  display: flex;
  flex-direction: column;
  gap: 30px;
  padding: 10px 0;
}

.step-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.step-icon {
  width: 28px;
  height: 28px;
  background-color: #ff9800;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
  font-size: 14px;
  margin-top: 0;
}

.step-content {
  flex: 1;
}

.step-text {
  font-size: 15px;
  color: #333;
  margin-bottom: 12px;
  font-weight: 500;
  line-height: 28px;
}

.qr-placeholder {
  width: 120px;
  height: 120px;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 5px;
}

.qr-code {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>
