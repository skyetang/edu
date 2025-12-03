<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NDataTable, NModal, NCard, NForm, NFormItem, NInput, NInputNumber, NSwitch, useMessage, NSpace, NSelect, useDialog, NIcon } from 'naive-ui'
import { CreateOutline, TrashOutline } from '@vicons/ionicons5'
import { getPlans, createPlan, updatePlan, deletePlan } from '@/api/membership'

const message = useMessage()
const dialog = useDialog()
const plans = ref([])
const loading = ref(false)
const showModal = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const unitOptions = [
  { label: '天', value: 'DAY' },
  { label: '周', value: 'WEEK' },
  { label: '月', value: 'MONTH' },
  { label: '年', value: 'YEAR' }
]

const formValue = ref({
  id: null,
  name: '',
  level: 1,
  price: 0,
  original_price: 0,
  duration_unit: 'MONTH',
  duration_value: 1,
  description: '',
  is_active: true
})

const rules = {
  name: { required: true, message: '请输入名称', trigger: 'blur' },
  level: { required: true, type: 'number', message: '请输入等级权重', trigger: 'blur' },
  price: { required: true, type: 'number', message: '请输入价格', trigger: 'blur' },
  duration_value: { required: true, type: 'number', message: '请输入有效期', trigger: 'blur' }
}

const columns = [
  { title: 'ID', key: 'id', width: 80, align: 'center' },
  { title: '名称', key: 'name', width: 150 },
  { title: '等级权重', key: 'level', width: 100, align: 'center' },
  { title: '价格', key: 'price', width: 100 },
  { title: '原价', key: 'original_price', width: 100 },
  { 
      title: '有效期', 
      key: 'duration_display',
      width: 120,
      render(row) {
          const unitMap = { 'DAY': '天', 'WEEK': '周', 'MONTH': '月', 'YEAR': '年' }
          if (row.duration_unit && row.duration_value) {
              return `${row.duration_value} ${unitMap[row.duration_unit]}`
          }
          return `${row.duration_days} 天`
      }
  },
  { title: '描述', key: 'description', minWidth: 200, ellipsis: true },
  { 
    title: '状态', 
    key: 'is_active',
    width: 100,
    align: 'center',
    render(row) {
      return row.is_active ? '启用' : '禁用'
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    align: 'center',
    fixed: 'right',
    render(row) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { 
              size: 'small', 
              quaternary: true,
              type: 'primary',
              onClick: () => handleEdit(row) 
          }, { 
              default: () => '编辑',
              icon: () => h(NIcon, null, { default: () => h(CreateOutline) })
          }),
          h(NButton, { 
              size: 'small', 
              quaternary: true,
              type: 'error', 
              onClick: () => handleDelete(row) 
          }, { 
              default: () => '删除',
              icon: () => h(NIcon, null, { default: () => h(TrashOutline) })
          })
        ]
      })
    }
  }
]

const fetchPlans = async () => {
  loading.value = true
  try {
    const res = await getPlans()
    plans.value = res
  } catch (error) {
    message.error('获取列表失败')
  } finally {
    loading.value = false
  }
}

const handleEdit = (row) => {
  isEdit.value = true
  formValue.value = { 
      ...row,
      price: Number(row.price),
      original_price: row.original_price ? Number(row.original_price) : 0,
      duration_unit: row.duration_unit || 'DAY', 
      duration_value: row.duration_value || row.duration_days 
  }
  showModal.value = true
}

const handleDelete = async (row) => {
  dialog.warning({
      title: '删除会员等级',
      content: '确定要删除这个会员等级吗？已关联的订单不会受影响，但新用户将无法购买此套餐。',
      positiveText: '确定删除',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
            await deletePlan(row.id)
            message.success('删除成功')
            fetchPlans()
        } catch (error) {
            message.error('删除失败')
        }
      }
  })
}

const handleSave = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      try {
        if (isEdit.value) {
          await updatePlan(formValue.value)
          message.success('更新成功')
        } else {
          await createPlan(formValue.value)
          message.success('创建成功')
        }
        showModal.value = false
        fetchPlans()
      } catch (error) {
        message.error('保存失败')
      }
    }
  })
}

const openCreate = () => {
  isEdit.value = false
  formValue.value = {
    id: null,
    name: '',
    level: 1,
    price: 0,
    original_price: 0,
    duration_unit: 'MONTH',
    duration_value: 1,
    description: '',
    is_active: true
  }
  showModal.value = true
}

onMounted(() => {
  fetchPlans()
})
</script>

<template>
  <div class="page-container">
    <div class="header-row">
      <div class="section-title">会员等级设置</div>
      <n-button type="primary" @click="openCreate">创建会员</n-button>
    </div>
    <n-data-table :columns="columns" :data="plans" :loading="loading" />

    <n-modal v-model:show="showModal">
      <n-card
        class="modal-card"
        :bordered="false"
        size="large"
        role="dialog"
        aria-modal="true"
      >
        <div class="modal-header">
          <div class="modal-title">{{ isEdit ? '编辑会员' : '创建会员' }}</div>
          <div class="modal-subtitle">设置会员等级权限与价格</div>
        </div>
        
        <n-form ref="formRef" :model="formValue" :rules="rules" label-placement="left" label-width="100px" size="large">
          <n-form-item label="名称" path="name">
            <n-input v-model:value="formValue.name" placeholder="如：VIP会员" />
          </n-form-item>
          <n-form-item label="等级权重" path="level">
            <n-input-number v-model:value="formValue.level" placeholder="数字越大权限越高" style="width: 100%" :show-button="false" />
          </n-form-item>
          <n-form-item label="价格" path="price">
            <n-input-number v-model:value="formValue.price" :precision="2" placeholder="0.00" style="width: 100%" :show-button="false">
                <template #prefix>¥</template>
            </n-input-number>
          </n-form-item>
          <n-form-item label="原价" path="original_price">
            <n-input-number v-model:value="formValue.original_price" :precision="2" placeholder="0.00" style="width: 100%" :show-button="false">
                <template #prefix>¥</template>
            </n-input-number>
          </n-form-item>
          <n-form-item label="有效期" path="duration_value">
              <n-input-number v-model:value="formValue.duration_value" placeholder="数值" style="width: 60%; margin-right: 10px;" :min="1" :show-button="false" />
              <n-select v-model:value="formValue.duration_unit" :options="unitOptions" style="width: 40%;" />
          </n-form-item>
          <n-form-item label="描述" path="description">
            <n-input v-model:value="formValue.description" type="textarea" placeholder="权限描述" />
          </n-form-item>
          <n-form-item label="启用" path="is_active">
            <n-switch v-model:value="formValue.is_active" />
          </n-form-item>
          
          <div class="modal-actions">
            <n-button @click="showModal = false" size="large" style="margin-right: 12px;">取消</n-button>
            <n-button type="primary" @click="handleSave" size="large">保存</n-button>
          </div>
        </n-form>
      </n-card>
    </n-modal>
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

.modal-card {
  width: 500px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.modal-header {
  text-align: center;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.modal-subtitle {
  font-size: 14px;
  color: #999;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
}

:deep(.n-data-table-th) {
  font-weight: 700;
  color: #333;
}

:deep(.n-data-table-td) {
  font-size: 13px;
}
</style>
