<script setup>
import { h, ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NDataTable, NTag, NButton, NIcon, NSpace, useMessage, NCountdown, NTime, useDialog } from 'naive-ui'
import { 
  CardOutline, 
  SparklesOutline,
  RepeatOutline,
  ArrowUpCircleOutline,
  TimeOutline, 
  CheckmarkCircleOutline, 
  CloseCircleOutline, 
  WalletOutline, 
  AlertCircleOutline
} from '@vicons/ionicons5'
import { getOrders, cancelOrder } from '@/api/membership'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const data = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page) => {
    pagination.page = page
    fetchOrders()
  },
  onUpdatePageSize: (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    fetchOrders()
  }
})

const columns = [
  {
    title: '订单号',
    key: 'order_no',
    width: 200
  },
  {
    title: '会员等级',
    key: 'plan_name',
    width: 150
  },
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
  {
    title: '时长(天)',
    key: 'plan_days',
    width: 100,
    align: 'center'
  },
  {
    title: '金额',
    key: 'amount',
    width: 100,
    render(row) {
        return `¥${row.amount}`
    }
  },
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
      
      return h(
        NTag,
        {
          type: config.type,
          bordered: false,
          size: 'small'
        },
        { 
          default: () => config.label,
          icon: () => h(NIcon, null, { default: () => h(config.icon) })
        }
      )
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
      const actions = [
        h(
            NButton,
            {
            size: 'small',
            type: row.status === 'PENDING' ? 'primary' : 'info',
            onClick: () => handleView(row)
            },
            {
            default: () => row.status === 'PENDING' ? '去支付' : '查看'
            }
        )
      ]

      if (row.status === 'PENDING') {
          actions.push(
              h(
                  NButton,
                  {
                      size: 'small',
                      type: 'error',
                      onClick: () => handleCancel(row)
                  },
                  {
                      default: () => '取消'
                  }
              )
          )
      }
      return h(NSpace, { justify: 'center' }, { default: () => actions })
    }
  }
]

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await getOrders({ 
        scope: 'my',
        page: pagination.page,
        page_size: pagination.pageSize
    })
    if (res.data) {
        data.value = res.data
        if (res.meta && res.meta.pagination) {
            pagination.itemCount = res.meta.pagination.total
        } else {
            pagination.itemCount = res.data.length
        }
    } else if (Array.isArray(res)) {
        data.value = res
        pagination.itemCount = res.length
    } else if (res.results) {
        data.value = res.results
        pagination.itemCount = res.count
    } else {
        data.value = []
        pagination.itemCount = 0
    }
  } catch (error) {
    message.error('获取订单失败')
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  router.push({ name: 'order-detail', query: { order_no: row.order_no } })
}

const handleCancel = async (row) => {
    dialog.warning({
        title: '取消订单',
        content: '确定要取消这个订单吗？取消后将无法恢复。',
        positiveText: '确定取消',
        negativeText: '暂不取消',
        onPositiveClick: async () => {
            try {
                await cancelOrder(row.order_no)
                message.success('订单已取消')
                fetchOrders()
            } catch (error) {
                message.error('取消失败')
            }
        }
    })
}

onMounted(() => {
  fetchOrders()
})
</script>

<template>
  <div class="my-orders">
    <n-card :bordered="false" class="page-card">
      <div class="card-header">
        <div class="section-title">我的订单</div>
      </div>
      <n-data-table
        :columns="columns"
        :data="data"
        :loading="loading"
        :bordered="true"
        :pagination="pagination"
        remote
      />
    </n-card>
  </div>
</template>

<style scoped>
.page-card {
  min-height: calc(100vh - 120px);
}

.card-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  border-left: 4px solid #f0a020;
  padding-left: 12px;
}

:deep(.n-data-table .n-data-table-th) {
  background-color: #fafafc;
  font-weight: 700;
  color: #333;
}

:deep(.n-data-table-td) {
  font-size: 13px;
}
</style>
