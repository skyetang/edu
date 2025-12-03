<script setup>
import { ref, reactive, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useMessage, NCard, NAvatar, NButton, NForm, NFormItem, NInput, NSpace, NUpload, NIcon } from 'naive-ui'
import { CreateOutline, PersonOutline, CallOutline, RibbonOutline, TimeOutline } from '@vicons/ionicons5'
import defaultAvatarImg from '@/assets/default.png'

const authStore = useAuthStore()
const message = useMessage()

const isEditing = ref(false)
const editForm = reactive({
    nickname: ''
})
const loading = ref(false)
const pendingAvatarFile = ref(null)
const previewAvatar = ref(null)

const fileInputRef = ref(null)

const userLevelDisplay = computed(() => {
  const user = authStore.user
  if (!user) return '未知'
  if (user.is_staff || user.is_superuser) return '管理员'
  
  const expireDate = user.membership_expire_at
  const isVip = expireDate && new Date(expireDate) > new Date()
  
  if (isVip) return user.level_display || 'VIP会员'
  return '普通用户'
})

const handleEdit = () => {
    editForm.nickname = authStore.user.nickname || ''
    isEditing.value = true
}

const cancelEdit = () => {
    isEditing.value = false
    pendingAvatarFile.value = null
    previewAvatar.value = null
}

const saveProfile = async () => {
    loading.value = true
    try {
        if (pendingAvatarFile.value) {
             await authStore.uploadAvatar(pendingAvatarFile.value)
        }
        
        if (editForm.nickname !== authStore.user.nickname) {
            await authStore.updateProfile({ nickname: editForm.nickname })
        }
        
        message.success('修改成功')
        isEditing.value = false
        pendingAvatarFile.value = null
        previewAvatar.value = null
    } catch (error) {
        if (!error.isGloballyHandled) {
            message.error(error.message || '修改失败')
        }
    } finally {
        loading.value = false
    }
}

const triggerUpload = () => {
    if (isEditing.value) {
        fileInputRef.value?.click()
    }
}

const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    // Basic validation
    if (!file.type.startsWith('image/')) {
        message.error('请选择图片文件')
        return
    }
    if (file.size > 2 * 1024 * 1024) {
        message.error('图片大小不能超过2MB')
        return
    }

    pendingAvatarFile.value = file
    
    const reader = new FileReader()
    reader.onload = (e) => {
        previewAvatar.value = e.target.result
    }
    reader.readAsDataURL(file)
    
    // Clear input so same file can be selected again if needed
    event.target.value = ''
}
</script>

<template>
  <div class="personal-settings-page">
    <div class="section-title">个人设置</div>
    
    <div class="settings-container">
        <div class="settings-card">
            <div class="card-header-bg"></div>
            
            <div class="profile-content">
                <div class="avatar-wrapper" :class="{ 'is-editing': isEditing }" @click="triggerUpload">
                    <n-avatar 
                        :src="previewAvatar || authStore.user?.avatar || defaultAvatarImg" 
                        :size="100" 
                        round
                        class="profile-avatar"
                        :img-props="{ alt: 'avatar' }"
                    />
                    <div class="avatar-overlay" v-if="isEditing">
                        <n-icon size="24" color="#fff"><CreateOutline /></n-icon>
                    </div>
                </div>
                <input 
                    type="file" 
                    ref="fileInputRef" 
                    style="display: none" 
                    accept="image/*"
                    @change="handleFileChange"
                />

                <div class="info-section">
                    <div class="info-item">
                        <div class="info-icon"><n-icon><PersonOutline /></n-icon></div>
                        <div class="info-content" :class="{ 'edit-mode': isEditing }">
                            <span class="label">昵称</span>
                            <n-input v-if="isEditing" v-model:value="editForm.nickname" placeholder="输入昵称" />
                            <span v-else class="value">{{ authStore.user?.nickname || '未设置昵称' }}</span>
                        </div>
                    </div>

                    <div class="info-item">
                        <div class="info-icon"><n-icon><RibbonOutline /></n-icon></div>
                        <div class="info-content">
                            <span class="label">用户级别</span>
                            <div class="value">
                                <span class="user-level-badge">{{ userLevelDisplay }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="info-item">
                        <div class="info-icon"><n-icon><CallOutline /></n-icon></div>
                        <div class="info-content">
                            <span class="label">手机号</span>
                            <span class="value">{{ authStore.user?.phone }}</span>
                        </div>
                    </div>

                    <div class="info-item">
                        <div class="info-icon"><n-icon><TimeOutline /></n-icon></div>
                        <div class="info-content">
                            <span class="label">注册时间</span>
                            <span class="value">{{ authStore.user?.date_joined ? new Date(authStore.user.date_joined).toLocaleDateString() : '未知' }}</span>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <n-button v-if="!isEditing" type="primary" color="#18a058" class="action-btn" @click="handleEdit">编辑资料</n-button>
                    <n-space v-else>
                        <n-button class="action-btn" @click="cancelEdit" :disabled="loading">取消</n-button>
                        <n-button type="primary" color="#18a058" class="action-btn" @click="saveProfile" :loading="loading">保存更改</n-button>
                    </n-space>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
.personal-settings-page {
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

.settings-container {
    max-width: 800px;
}

.settings-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
    border: 1px solid #eee;
    max-width: 500px;
    overflow: hidden;
    position: relative;
}

.card-header-bg {
    height: 120px;
    background: linear-gradient(135deg, #18a058 0%, #2080f0 100%);
    opacity: 0.9;
}

.profile-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 40px 40px;
    margin-top: -50px; /* Overlap avatar */
    position: relative;
    z-index: 1;
}

.avatar-wrapper {
    position: relative;
    margin-bottom: 20px;
    border-radius: 50%;
    padding: 4px;
    background: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.avatar-wrapper.is-editing {
    cursor: pointer;
}

.profile-avatar {
    display: block;
}

.avatar-overlay {
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s;
}

.avatar-wrapper:hover .avatar-overlay {
    opacity: 1;
}

.user-level-badge {
    color: #18a058;
    font-weight: 600;
    font-size: 14px;
    background: rgba(24, 160, 88, 0.1);
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
}

.info-section {
    width: 100%;
    max-width: 360px;
    margin: 0 auto 30px;
}

.info-item {
    display: flex;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
    border-bottom: none;
}

.info-icon {
    width: 40px;
    height: 40px;
    background: #f9f9f9;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    color: #666;
    font-size: 18px;
}

.info-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.info-content.edit-mode {
    flex-direction: row;
    align-items: center;
    gap: 10px;
}

.info-content.edit-mode .label {
    width: 60px;
    margin-bottom: 0;
}

.label {
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
}

.value {
    font-size: 16px;
    color: #333;
    font-weight: 500;
}

.actions {
    width: 100%;
    display: flex;
    justify-content: center;
}

.action-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    border-radius: 8px;
}
</style>
