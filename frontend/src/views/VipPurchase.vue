<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
    NButton, NCard, NGrid, NGridItem, NTag, 
    useMessage, NIcon, NCollapse, NCollapseItem,
    NSpace
} from 'naive-ui'
import { 
    CheckmarkCircle, 
    HelpCircleOutline,
    DiamondOutline,
    Star,
    LibraryOutline,
    CodeSlashOutline,
    PeopleOutline
} from '@vicons/ionicons5'
import { getPlans, createOrder } from '@/api/membership'
import { getProfile } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const message = useMessage()

const plans = ref([])
const loading = ref(false)

const fetchPlans = async () => {
    loading.value = true
    try {
        const res = await getPlans()
        plans.value = res
    } catch (error) {
        console.error(error)
        message.error('获取会员套餐失败')
    } finally {
        loading.value = false
    }
}

const fetchUserProfile = async () => {
    if (authStore.isLoggedIn) {
        try {
            const user = await getProfile()
            authStore.user = user
        } catch (error) {
            console.error('Failed to refresh profile', error)
        }
    }
}

const getButtonState = (plan) => {
    const user = authStore.user
    
    // Not logged in or no user info
    if (!user) {
        return { text: '立即开通', type: 'primary', disabled: false, visible: true }
    }

    // Check expiration
    const now = new Date()
    const expireAt = user.membership_expire_at ? new Date(user.membership_expire_at) : null
    const isVip = expireAt && expireAt > now
    
    if (!isVip) {
        return { text: '立即开通', type: 'primary', disabled: false, visible: true }
    }
    
    // Is VIP, compare levels
    const userLevel = Number(user.level || 0)
    const planLevel = Number(plan.level)
    
    if (userLevel === planLevel) {
        return { text: '续费会员', type: 'primary', disabled: false, visible: true }
    } else if (userLevel < planLevel) {
        return { text: '升级会员', type: 'warning', disabled: false, visible: true }
    } else {
        // userLevel > planLevel: Downgrade not supported
        return { text: '', type: 'default', disabled: true, visible: false }
    }
}

const handleBuy = async (plan) => {
    if (!authStore.isLoggedIn) {
        message.warning('请先登录')
        // Assuming you have a way to trigger login modal or redirect
        router.push('/login') 
        return
    }
    
    try {
        const res = await createOrder(plan.id)
        if (res && res.order_no) {
            router.push({ 
                name: 'order-detail', 
                query: { order_no: res.order_no } 
            })
        }
    } catch (error) {
        message.error(error.message || '创建订单失败')
        if (error.message && error.message.includes('未支付')) {
            setTimeout(() => {
                router.push({ name: 'my-orders' })
            }, 1500)
        }
    }
}

const parseBenefits = (desc) => {
    if (!desc) return []
    return desc.split('\n').filter(item => item.trim())
}

const getDiscount = (price, original) => {
    if (!original || Number(original) <= Number(price)) return null
    return (Number(price) / Number(original) * 10).toFixed(1)
}

onMounted(() => {
    fetchPlans()
    fetchUserProfile()
})
</script>

<template>
    <div class="vip-page">
        <!-- Banner Section -->
        <div class="banner">
            <div class="banner-content">
                <div class="banner-text">
                    <h1><span class="highlight-text">VIP会员</span></h1>
                    <p class="subtitle">投资自己，开启无限可能的学习之旅</p>
                    <div class="banner-benefits">
                        <div class="benefit-item-banner">
                            <div class="icon-box"><n-icon><LibraryOutline /></n-icon></div>
                            <div class="text-box">
                                <div class="title">海量课程</div>
                                <div class="desc">全站付费课程免费看</div>
                            </div>
                        </div>
                        <div class="benefit-item-banner">
                            <div class="icon-box"><n-icon><CodeSlashOutline /></n-icon></div>
                            <div class="text-box">
                                <div class="title">高清源码</div>
                                <div class="desc">配套课件源码下载</div>
                            </div>
                        </div>
                        <div class="benefit-item-banner">
                            <div class="icon-box"><n-icon><PeopleOutline /></n-icon></div>
                            <div class="text-box">
                                <div class="title">专属社群</div>
                                <div class="desc">技术大牛在线答疑</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="banner-icon-wrapper">
                    <div class="icon-container">
                         <n-icon size="160" color="rgba(255,255,255,0.9)" class="dynamic-icon">
                            <DiamondOutline />
                        </n-icon>
                    </div>
                    <div class="floating-star star-1"><n-icon size="28" color="#ffd700"><Star /></n-icon></div>
                    <div class="floating-star star-2"><n-icon size="20" color="#fff"><Star /></n-icon></div>
                    <div class="floating-star star-3"><n-icon size="24" color="#ffecb3"><Star /></n-icon></div>
                </div>
            </div>
        </div>

        <!-- Membership Cards -->
        <div class="cards-container">
            <div class="section-header">
                <h2>会员权益对比</h2>
                <div class="title-line"></div>
            </div>

            <div class="cards-grid">
                <div 
                    v-for="plan in plans" 
                    :key="plan.id" 
                    class="plan-card"
                    :class="{ 'highlight': plan.is_highlight }"
                >
                    <div class="card-header">
                        <div class="plan-name">{{ plan.name }}</div>
                        <div class="price-section">
                            <div v-if="plan.original_price > Number(plan.price)" class="original-price">
                                原价: <span class="strike">¥{{ plan.original_price }}</span>
                                <span class="discount-tag">限时{{ getDiscount(plan.price, plan.original_price) }}折</span>
                            </div>
                            <div class="current-price">
                                <span class="symbol">¥</span>
                                <span class="amount">{{ Number(plan.price) }}</span>
                                <span class="unit">/ {{ plan.duration_unit === 'MONTH' ? '月' : plan.duration_unit === 'YEAR' ? '年' : '期' }}</span>
                            </div>
                            <div v-if="plan.original_price > Number(plan.price)" class="save-tip">
                                立省 ¥{{ (plan.original_price - plan.price).toFixed(0) }}
                            </div>
                        </div>
                    </div>

                    <div class="benefits-list">
                        <div v-for="(benefit, index) in parseBenefits(plan.description)" :key="index" class="benefit-item">
                            <n-icon color="#52c41a" size="18">
                                <CheckmarkCircle />
                            </n-icon>
                            <span>{{ benefit }}</span>
                        </div>
                    </div>

                    <div class="card-action" v-if="getButtonState(plan).visible">
                        <n-button 
                            :type="getButtonState(plan).type" 
                            class="buy-btn" 
                            :color="plan.is_highlight && getButtonState(plan).text === '立即开通' ? '#ff7d18' : undefined"
                            round
                            size="large"
                            :disabled="getButtonState(plan).disabled"
                            @click="handleBuy(plan)"
                        >
                            {{ getButtonState(plan).text }}
                        </n-button>
                    </div>
                    <div class="card-action" v-else>
                         <!-- Placeholder for layout stability or message -->
                         <div style="height: 48px; display: flex; align-items: center; justify-content: center; color: #999; font-size: 14px;">
                             当前等级更高
                         </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- FAQ Section -->
        <div class="faq-section">
            <div class="section-header">
                <h2>常见问题</h2>
                <div class="title-line"></div>
            </div>
            
            <div class="faq-list">
                <div class="faq-item">
                    <div class="question">
                        <span class="q-icon">Q</span>
                        <span>支持哪些支付方式？</span>
                    </div>
                    <div class="answer">
                        <span class="a-icon">A</span>
                        <span>目前仅支持支付宝/微信在线支付，如需其他支付方式，请联系客服。</span>
                    </div>
                </div>
                <div class="faq-item">
                    <div class="question">
                        <span class="q-icon">Q</span>
                        <span>购买后多久生效？</span>
                    </div>
                    <div class="answer">
                        <span class="a-icon">A</span>
                        <span>购买成功后立即生效，您可以在个人中心查看对应的VIP权益。</span>
                    </div>
                </div>
                <div class="faq-item">
                    <div class="question">
                        <span class="q-icon">Q</span>
                        <span>支持退款吗？</span>
                    </div>
                    <div class="answer">
                        <span class="a-icon">A</span>
                        <span>虚拟商品，购买后立即生效，不支持退款。请您在购买之前确认好需求。</span>
                    </div>
                </div>
                <div class="faq-item">
                    <div class="question">
                        <span class="q-icon">Q</span>
                        <span>会员期限如何计算？</span>
                    </div>
                    <div class="answer">
                        <span class="a-icon">A</span>
                        <span>会员期限从购买成功之日起计算。例如购买1年会员，有效期为365天。</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.vip-page {
    min-height: 100vh;
    padding-bottom: 60px;
    padding-top: 20px;
}

.banner {
    height: 300px;
    background: linear-gradient(135deg, #ff7d18 0%, #ff4d4f 100%);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    max-width: 1200px;
    margin: 0 auto;
    border-radius: 20px;
}

.banner-content {
    width: 100%;
    padding: 40px 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 2;
    position: relative;
}

.banner-text {
    text-align: left;
    flex: 1;
    z-index: 5;
}

.banner h1 {
    font-size: 56px;
    margin-top: 0;
    margin-bottom: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    text-shadow: 0 4px 16px rgba(0,0,0,0.15);
    line-height: 1.1;
    display: flex;
    align-items: center;
}

.highlight-text {
    color: #fff;
    background: linear-gradient(180deg, #fff 0%, #ffecb3 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    margin-right: 10px;
    font-style: italic;
}

.banner .subtitle {
    font-size: 20px;
    opacity: 0.9;
    margin-bottom: 40px;
    font-weight: 400;
    letter-spacing: 0.5px;
    max-width: 600px;
}

.banner-benefits {
    display: flex;
    gap: 30px;
}

.benefit-item-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.1);
    padding: 12px 20px;
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    transition: all 0.3s ease;
}

.benefit-item-banner:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.icon-box {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    flex-shrink: 0;
}

.icon-box .n-icon {
    font-size: 24px;
    color: #ff7d18;
}

.text-box {
    display: flex;
    flex-direction: column;
    text-align: left;
}

.text-box .title {
    font-size: 16px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 2px;
}

.text-box .desc {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
}

.banner-icon-wrapper {
    position: relative;
    width: 300px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 40px;
    flex-shrink: 0;
}

.icon-container {
    filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.3));
}

.dynamic-icon {
    display: block;
    animation: float 6s ease-in-out infinite;
}

.floating-star {
    position: absolute;
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.8));
    animation: twinkle 3s infinite alternate;
}

.star-1 { top: 15%; right: 15%; animation-delay: 0s; }
.star-2 { bottom: 20%; left: 10%; animation-delay: 1s; }
.star-3 { top: 30%; left: 25%; animation-delay: 2s; }

.cards-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0;
    position: relative;
    z-index: 10;
}

.section-header {
    text-align: center;
    margin-bottom: 40px;
    margin-top: 50px;
}

.section-header h2 {
    font-size: 28px;
    color: #333;
    font-weight: 700;
    margin-bottom: 10px;
}

.cards-container .section-header {
    margin-top: 50px;
    margin-bottom: 40px;
    display: block;
}

.cards-grid {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.plan-card {
    background: #fff;
    border-radius: 16px;
    flex: 1;
    min-width: 300px;
    padding: 40px 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    transition: transform 0.3s, box-shadow 0.3s;
    display: flex;
    flex-direction: column;
    position: relative;
    border: 1px solid transparent;
}

.plan-card:first-child {
    margin-left: 0;
}

.plan-card:last-child {
    margin-right: 0;
}


.plan-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.plan-card.highlight {
    border-color: #ff7d18;
    transform: scale(1.05);
    z-index: 2;
}

.card-header {
    text-align: center;
    margin-bottom: 24px;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 20px;
}

.plan-name {
    font-size: 24px;
    font-weight: 700;
    color: #333;
    margin-bottom: 20px;
}

.original-price {
    font-size: 14px;
    color: #999;
    margin-bottom: 12px;
}

.strike {
    text-decoration: line-through;
}

.discount-tag {
    background: #ff4d4f;
    color: #fff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    margin-left: 8px;
}

.current-price {
    color: #ff7d18;
    display: flex;
    align-items: baseline;
    justify-content: center;
    margin: 5px 0;
}

.current-price .symbol {
    font-size: 24px;
    font-weight: 500;
}

.current-price .amount {
    font-size: 56px;
    font-weight: 500;
    line-height: 1;
    margin: 0 4px;
    letter-spacing: -1px;
}

.current-price .unit {
    font-size: 16px;
    color: #666;
    font-weight: 400;
}

.save-tip {
    font-size: 14px;
    color: #52c41a;
    margin-top: 16px;
    font-weight: 500;
    background: rgba(82, 196, 26, 0.1);
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
}

.benefits-list {
    flex: 1;
    margin-bottom: 24px;
}

.benefit-item {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    color: #666;
    font-size: 15px;
    line-height: 1.6;
}

.benefit-item .n-icon {
    margin-right: 8px;
    flex-shrink: 0;
}

.buy-btn {
    width: 66%;
    font-weight: 600;
    height: 48px;
    font-size: 16px;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.buy-btn::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    transform: skewX(-20deg);
    transition: left 0.6s ease;
    pointer-events: none;
}

.buy-btn:hover::after {
    left: 100%;
}

.card-action {
    text-align: center;
}

.faq-section {
    max-width: 1200px;
    margin: 60px auto 0;
    padding: 0 20px;
}

.title-line {
    width: 40px;
    height: 4px;
    background: #ff7d18;
    margin: 0 auto;
    border-radius: 2px;
}

.faq-list {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}

.faq-item {
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid #f5f5f5;
}

.faq-item:last-child {
    margin-bottom: 0;
    border-bottom: none;
    padding-bottom: 0;
}

.question {
    display: flex;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 12px;
}

.q-icon {
    background: #ff7d18;
    color: #fff;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    margin-right: 10px;
    font-weight: 700;
}

.answer {
    display: flex;
    align-items: flex-start;
    font-size: 14px;
    color: #666;
    line-height: 1.6;
}

.a-icon {
    background: #f5f5f5;
    color: #999;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    margin-right: 10px;
    font-weight: 700;
    flex-shrink: 0;
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
    100% { transform: translateY(0px); }
}

@keyframes twinkle {
    0% { opacity: 0.3; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1.2); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .banner {
        height: auto;
        min-height: auto;
        padding: 40px 20px;
    }
    
    .banner-content {
        flex-direction: column;
        padding: 0;
        text-align: center;
    }
    
    .banner-text {
        text-align: center;
    }
    
    .banner h1 {
        justify-content: center;
        font-size: 36px;
    }
    
    .banner .subtitle {
        margin-left: auto;
        margin-right: auto;
        font-size: 16px;
    }
    
    .banner-benefits {
        flex-direction: column;
        gap: 15px;
        align-items: stretch;
    }
    
    .benefit-item-banner {
        justify-content: flex-start;
    }
    
    .banner-icon-wrapper {
        margin-left: 0;
        margin-top: 40px;
        width: 100%;
        height: 200px;
    }
    
    .cards-grid {
        flex-direction: column;
        gap: 30px;
    }
    
    .plan-card {
        margin: 0 !important;
        width: 100%;
    }
    
    .plan-card.highlight {
        transform: none;
    }
    
    .cards-container {
        padding: 0 20px;
    }

    .faq-section {
        margin-top: 40px;
    }
}
</style>