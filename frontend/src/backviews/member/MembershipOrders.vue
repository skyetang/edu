<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NDataTable, useMessage, NTag, NSpace, NTime, NCountdown, NIcon, useDialog } from 'naive-ui'
import { 
  TimeOutline, 
  CheckmarkCircleOutline, 
  CloseCircleOutline, 
  WalletOutline, 
  AlertCircleOutline,
  TrashOutline,
  CardOutline,
  PersonOutline,
  SparklesOutline,
  RepeatOutline,
  ArrowUpCircleOutline,
  EyeOutline
} from '@vicons/ionicons5'
import { getOrders, cancelOrder, refundOrder } from '@/api/membership'
import { useRouter } from 'vue-router'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const orders = ref([])
const loading = ref(false)

const columns = [
  { title: '订单号', key: 'order_no', width: 200 },
  { title: '用户手机', key: 'user_phone', width: 140 },
  { 
    title: '用户昵称', 
    key: 'user_nickname', 
    width: 140,
    render(row) {
       return row.user_nickname || '-'
    }
  },
  { title: '套餐', key: 'plan_name', width: 120 },
  {
    title: '订单类型',
    key: 'order_type',
    width: 120,
    render(row) {
        const typeConfig = {
            'NEW': { icon: SparklesOutline, label: '新购', color: '#2080f0' },
            'RENEWAL': { icon: RepeatOutline, label: '续费', color: '#18a058' },
            'UPGRADE': { icon: ArrowUpCircleOutline, label: '升级', color: '#f0a020' }
        }
        const config = typeConfig[row.order_type] || { icon: CardOutline, label: '未知', color: '#999' }
        
        return h(NSpace, { align: 'center', size: 4 }, {
            default: () => [
                h(NIcon, { size: 18, color: config.color }, { default: () => h(config.icon) }),
                h('span', { style: { color: config.color } }, config.label)
            ]
        })
    }
  },
  { title: '金额', key: 'amount', width: 100 },
  { 
    title: '状态', 
    key: 'status_display',
    width: 140,
    align: 'center',
    render(row) {
      const statusConfig = {
        'PENDING': { type: 'warning', icon: TimeOutline, label: '待支付' },
        'PAID': { type: 'success', icon: CheckmarkCircleOutline, label: '已支付' },
        'CANCELLED': { type: 'default', icon: CloseCircleOutline, label: '已取消' },
        'REFUNDED': { type: 'error', icon: WalletOutline, label: '已退款' },
        'EXPIRED': { type: 'default', icon: AlertCircleOutline, label: '已失效' }
      }
      const config = statusConfig[row.status] || { type: 'default', icon: AlertCircleOutline, label: row.status }
      return h(NTag, { 
          type: config.type, 
          bordered: false, 
          round: true, 
          size: 'small',
          style: { padding: '0 12px' }
      }, { 
          default: () => config.label,
          icon: () => h(NIcon, null, { default: () => h(config.icon) })
      })
    }
  },
  { 
    title: '创建时间', 
    key: 'created_at',
    width: 180,
    render(row) {
        return h(NTime, { time: new Date(row.created_at) })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    align: 'center',
    fixed: 'right',
    render(row) {
      const actions = []
      
      actions.push(h(NButton, { 
          size: 'small', 
          quaternary: true,
          type: 'info',
          onClick: () => router.push({ name: 'order-detail', query: { order_no: row.order_no } })
      }, { 
          default: () => '查看',
          icon: () => h(NIcon, null, { default: () => h(EyeOutline) })
      }))

      if (row.status === 'PENDING') {
        actions.push(h(NButton, { 
            size: 'small', 
            quaternary: true,
            type: 'error',
            onClick: () => handleCancel(row) 
        }, { 
            default: () => '取消订单',
            icon: () => h(NIcon, null, { default: () => h(CloseCircleOutline) })
        }))
      }
      if (row.status === 'PAID') {
        actions.push(h(NButton, { 
            size: 'small', 
            quaternary: true,
            type: 'error', 
            onClick: () => handleRefund(row) 
        }, { 
            default: () => '退款',
            icon: () => h(NIcon, null, { default: () => h(WalletOutline) })
        }))
      }
      return h(NSpace, null, { default: () => actions })
    }
  }
]

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders()
    orders.value = res
  } catch (error) {
    if (!error.isGloballyHandled) {
        message.error('获取订单失败')
    }
  } finally {
    loading.value = false
  }
}

const handleCancel = async (row) => {
  dialog.warning({
      title: '取消订单',
      content: '确定要强制取消此订单吗？',
      positiveText: '确定取消',
      negativeText: '点错了',
      onPositiveClick: async () => {
        try {
            await cancelOrder(row.order_no)
            message.success('订单已取消')
            fetchOrders()
        } catch (error) {
            if (!error.isGloballyHandled) {
                message.error('取消失败')
            }
        }
      }
  })
}

const handleRefund = async (row) => {
  dialog.error({
      title: '确认退款',
      content: `确定要对订单 ${row.order_no} 进行退款吗？退款后会员权益将自动扣除。`,
      positiveText: '确认退款',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
            await refundOrder(row.order_no)
            message.success('退款成功')
            fetchOrders()
        } catch (error) {
            if (!error.isGloballyHandled) {
                message.error('退款失败')
            }
        }
      }
  })
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="page-container">
    <div class="header-row">
      <div class="section-title">会员订单列表</div>
    </div>
    <n-data-table :columns="columns" :data="orders" :loading="loading" />
  </div>
</template>

<style scoped>
.page-container {
  background-color: #fff;
  padding: 24px;
  border-radius: 8px;
  min-height: calc(100vh - 120px);
}

.header-row {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  border-left: 4px solid #f0a020;
  padding-left: 12px;
}

:deep(.n-data-table-th) {
  font-weight: 700;
  color: #333;
}

:deep(.n-data-table-td) {
  font-size: 13px;
}
</style>
