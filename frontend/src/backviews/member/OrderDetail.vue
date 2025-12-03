<script setup>
import { ref, onMounted, computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage, NIcon, NTag, NButton, NSpace, NCountdown } from 'naive-ui'
import { 
    LogoWechat, 
    CardOutline,
    CheckmarkCircle,
    TimeOutline,
    CheckmarkCircleOutline,
    CloseCircleOutline,
    WalletOutline,
    AlertCircleOutline,
    SparklesOutline,
    RepeatOutline,
    ArrowUpCircleOutline
} from '@vicons/ionicons5'
import { getOrderDetail, payOrder, cancelOrder } from '@/api/membership'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()
const order = ref(null)
const loading = ref(false)
const paymentMethod = ref('ALIPAY') 
const orderNo = route.query.order_no

const isOwner = computed(() => {
    return authStore.user && order.value && authStore.user.id === order.value.user
})

const fetchOrder = async () => {
  if (!orderNo) return
  loading.value = true
  try {
    const res = await getOrderDetail(orderNo)
    order.value = res
  } catch (error) {
    if (!error.isGloballyHandled) {
        message.error('获取订单详情失败')
    }
  } finally {
    loading.value = false
  }
}

const handlePay = async () => {
  try {
    await payOrder(orderNo, paymentMethod.value)
    message.success('支付成功')
    await authStore.fetchProfile()
    await fetchOrder() 
    setTimeout(() => {
        router.push({ name: 'my-member' })
    }, 1500)
  } catch (error) {
    if (!error.isGloballyHandled) {
        message.error('支付失败: ' + (error.message || '未知错误'))
    }
  }
}

const countdownDuration = computed(() => {
    if (!order.value || order.value.status !== 'PENDING') return 0
    const remaining = order.value.remaining_seconds
    if (remaining === undefined || remaining <= 0) return 0
    return remaining * 1000
})

const handleCountdownFinish = () => {
    // Just refresh order, don't show toast to avoid annoying user on page load
    fetchOrder()
}

const durationDisplay = computed(() => {
    if (!order.value) return ''
    // If plan_days is roughly a year (365 or 366), show 1 year
    if (order.value.plan_days >= 365) return '1年'
    // If roughly a month (28-31), show 1 month
    if (order.value.plan_days >= 28 && order.value.plan_days <= 31) return '1个月'
    return `${order.value.plan_days}天`
})

const typeConfig = computed(() => {
    if (!order.value) return {}
    const configs = {
        'NEW': { icon: SparklesOutline, label: '新购会员', color: '#2080f0' },
        'RENEWAL': { icon: RepeatOutline, label: '续费会员', color: '#18a058' },
        'UPGRADE': { icon: ArrowUpCircleOutline, label: '升级会员', color: '#f0a020' }
    }
    return configs[order.value.order_type] || { icon: CardOutline, label: '未知类型', color: '#999' }
})

const statusConfig = computed(() => {
    if (!order.value) return {}
    const configs = {
        'PENDING': { type: 'warning', icon: TimeOutline, label: '未支付', buttonText: '立即支付', buttonType: 'primary' },
        'PAID': { type: 'success', icon: CheckmarkCircleOutline, label: '已支付', buttonText: '支付成功', buttonType: 'success' },
        'CANCELLED': { type: 'default', icon: CloseCircleOutline, label: '已取消', buttonText: '订单已取消', buttonType: 'default' },
        'REFUNDED': { type: 'error', icon: WalletOutline, label: '已退款', buttonText: '订单已退款', buttonType: 'error' },
        'EXPIRED': { type: 'default', icon: AlertCircleOutline, label: '已失效', buttonText: '订单已过期', buttonType: 'error' }
    }
    return configs[order.value.status] || { type: 'default', icon: AlertCircleOutline, label: order.value.status, buttonText: order.value.status, buttonType: 'default' }
})

const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).replace(/\//g, '/')
}

const dynamicTime = computed(() => {
    if (!order.value) return { label: '-', value: '-' }
    
    const status = order.value.status
    
    if (status === 'PENDING') {
        const created = new Date(order.value.created_at)
        const expired = new Date(created.getTime() + 30 * 60000)
        return { label: '支付截止', value: formatDate(expired) }
    } else if (status === 'PAID') {
        return { label: '支付时间', value: formatDate(order.value.paid_at) }
    } else if (status === 'CANCELLED') {
        return { label: '取消时间', value: formatDate(order.value.updated_at) }
    } else if (status === 'REFUNDED') {
        return { label: '退款时间', value: formatDate(order.value.updated_at) }
    } else if (status === 'EXPIRED') {
        const created = new Date(order.value.created_at)
        const expired = new Date(created.getTime() + 30 * 60000)
        return { label: '失效时间', value: formatDate(expired) }
    }
    return { label: '更新时间', value: formatDate(order.value.updated_at) }
})

onMounted(() => {
  fetchOrder()
})
</script>

<template>
  <div class="order-page">
    <div v-if="order" class="content-container">
        <!-- Order Info Card -->
        <div class="order-card">
            <!-- Header -->
            <div class="card-header">
                <div class="header-title">订单详情</div>
                <div class="header-status">
                    <n-tag :type="statusConfig.type" round :bordered="false" size="large" style="padding: 0 20px; justify-content: center;">
                        <div style="display: flex; align-items: center; gap: 4px;">
                            <n-icon size="20" :component="statusConfig.icon" />
                            <span>{{ statusConfig.label }}</span>
                        </div>
                    </n-tag>
                </div>
            </div>

            <!-- Details List -->
            <div class="details-list">
                <div class="detail-row">
                    <div class="label">订单号</div>
                    <div class="value">{{ order.order_no }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">用户昵称</div>
                    <div class="value">{{ order.user_nickname || '-' }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">用户手机</div>
                    <div class="value">{{ order.user_phone || '-' }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">订单类型</div>
                    <div class="value type-value">
                        <n-icon :component="typeConfig.icon" :color="typeConfig.color" size="18" style="position: relative; top: 1px;" />
                        <span :style="{ color: typeConfig.color }">{{ typeConfig.label }}</span>
                    </div>
                </div>

                <div class="detail-row">
                    <div class="label">会员等级</div>
                    <div class="value">{{ order.plan_name }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">开通时长</div>
                    <div class="value">{{ durationDisplay }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">订单金额</div>
                    <div class="value amount">¥{{ order.amount }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">创建时间</div>
                    <div class="value">{{ formatDate(order.created_at) }}</div>
                </div>

                <div class="detail-row">
                    <div class="label">{{ dynamicTime.label }}</div>
                    <div class="value">{{ dynamicTime.value }}</div>
                </div>
            </div>

            <!-- Non-pending or Non-owner Footer -->
            <div v-if="order.status !== 'PENDING' || !isOwner" class="card-footer">
                <div class="status-banner" :class="order.status.toLowerCase()">
                    <n-icon size="24" :component="statusConfig.icon" />
                    <span>{{ !isOwner && order.status === 'PENDING' ? '等待用户支付' : statusConfig.buttonText }}</span>
                </div>
                <div class="back-link" @click="router.back()">
                    返回
                </div>
            </div>
        </div>

        <!-- Payment Card (Separate) -->
        <div v-if="order.status === 'PENDING' && isOwner" class="payment-section">
            <div class="payment-card">
                <div class="payment-header">
                    <span>选择支付方式</span>
                    <div v-if="countdownDuration > 0" class="countdown-timer">
                        <n-icon size="28"><TimeOutline /></n-icon>
                        <n-countdown :duration="countdownDuration" active @finish="handleCountdownFinish" />
                    </div>
                </div>
                <div class="payment-methods">
                    <div 
                        class="payment-item" 
                        :class="{ active: paymentMethod === 'ALIPAY' }"
                        @click="paymentMethod = 'ALIPAY'"
                    >
                        <div class="icon-wrapper alipay">
                            <n-icon size="28" color="#fff"><CardOutline /></n-icon>
                        </div>
                        <div class="payment-info">
                            <div class="payment-name">支付宝</div>
                            <div class="payment-desc">推荐使用支付宝支付</div>
                        </div>
                        <n-icon v-if="paymentMethod === 'ALIPAY'" size="24" color="#18a058"><CheckmarkCircle /></n-icon>
                    </div>
                    
                    <div 
                        class="payment-item" 
                        :class="{ active: paymentMethod === 'WECHAT' }"
                        @click="paymentMethod = 'WECHAT'"
                    >
                        <div class="icon-wrapper wechat">
                            <n-icon size="28" color="#fff"><LogoWechat /></n-icon>
                        </div>
                        <div class="payment-info">
                            <div class="payment-name">微信支付</div>
                            <div class="payment-desc">使用微信扫码支付</div>
                        </div>
                        <n-icon v-if="paymentMethod === 'WECHAT'" size="24" color="#18a058"><CheckmarkCircle /></n-icon>
                    </div>
                </div>
            </div>

            <n-button 
                block 
                type="primary" 
                size="large" 
                class="pay-btn"
                @click="handlePay"
                :disabled="countdownDuration <= 0"
            >
                <span>立即支付 ¥{{ order.amount }}</span>
            </n-button>
            
            <div class="back-link-center" @click="router.back()">
                暂不支付，返回
            </div>
        </div>
    </div>
    
    <div v-else-if="loading" class="loading-state">
        加载中...
    </div>
  </div>
</template>

<style scoped>
.order-page {
    min-height: calc(100vh - 60px);
    background-color: #f5f7fa;
    display: flex;
    justify-content: center;
    padding-top: 40px;
    padding-bottom: 60px;
}

.content-container {
    width: 600px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.order-card, .payment-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    padding: 30px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.header-title, .payment-header {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}

.payment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.header-status {
    display: flex;
    align-items: center;
    gap: 12px;
}

.countdown-timer {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #f0a020;
    font-size: 28px;
    font-weight: bold;
}

.details-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
    margin-bottom: 10px;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.detail-row .label {
    color: #666;
}

.detail-row .value {
    color: #333;
    font-weight: 500;
}

.detail-row .type-value {
    display: flex;
    align-items: center;
    gap: 6px;
}

.detail-row .amount {
    color: #f0a020;
    font-size: 18px;
    font-weight: bold;
}

/* Payment Section Styles */
.payment-section {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.payment-methods {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.payment-item {
    display: flex;
    align-items: center;
    padding: 20px;
    border: 1px solid #eee;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
    background: #fff;
    position: relative;
}

.payment-item:hover {
    border-color: #b0b0b0;
}

.payment-item.active {
    border-color: #18a058;
    background-color: #f6fffa;
}

.icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
}

.icon-wrapper.alipay {
    background-color: #1677ff;
}

.icon-wrapper.wechat {
    background-color: #07c160;
}

.payment-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.payment-name {
    font-size: 16px;
    font-weight: bold;
    color: #333;
}

.payment-desc {
    font-size: 13px;
    color: #999;
}

.pay-btn {
    height: 50px;
    font-size: 18px;
    border-radius: 8px;
    background-color: #18a058; /* Green pay button to match selection style or keep primary? Screenshot has green button */
    border: none;
}
.pay-btn:hover {
    background-color: #36ad6a;
}
.pay-btn[disabled] {
    background-color: #ccc;
}

/* Status Banner */
.status-banner {
    width: 100%;
    height: 48px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 500;
    color: #fff;
    margin-top: 20px;
}

.status-banner.paid { background-color: #18a058; }
.status-banner.cancelled { background-color: #999; }
.status-banner.refunded { background-color: #d03050; }
.status-banner.expired { background-color: #e88080; }

.card-footer {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

.back-link {
    color: #666;
    cursor: pointer;
    font-size: 14px;
}

.back-link-center {
    text-align: center;
    color: #666;
    cursor: pointer;
    font-size: 14px;
    margin-top: -10px;
}

.back-link:hover, .back-link-center:hover {
    color: #333;
    text-decoration: underline;
}

.loading-state {
    padding-top: 100px;
    color: #999;
}
</style>