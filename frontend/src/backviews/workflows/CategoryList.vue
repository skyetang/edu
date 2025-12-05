<template>
  <div class="category-list">
    <n-card title="工作流分类管理">
      <template #header-extra>
        <n-button type="primary" @click="handleAdd(null)">
          添加一级分类
        </n-button>
      </template>

      <n-spin :show="loading">
        <div class="category-tree-container">
          <div v-if="!loading && categoryData.length === 0" class="empty-state">
            <n-empty description="暂无分类" />
          </div>
          
          <div v-else class="category-tree">
            <CategoryItem
              v-for="category in categoryData"
              :key="category.id"
              :data="category"
              :level="0"
              always-show-expand
              @add-sub="handleAdd"
              @edit="handleEdit"
              @delete="handleDelete"
            />
          </div>
        </div>
      </n-spin>
    </n-card>

    <!-- 添加/编辑分类弹窗 -->
    <n-modal v-model:show="showModal">
      <n-card
        class="auth-card category-modal"
        :bordered="false"
        size="large"
        role="dialog"
        aria-modal="true"
        closable
        @close="showModal = false"
      >
        <template #header>
          <div class="modal-title">{{ modalTitle }}</div>
        </template>
        <n-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-placement="left"
          label-width="100"
        >
          <n-form-item label="父级分类" v-if="formData.parentName">
            <n-input v-model:value="formData.parentName" disabled size="large" />
          </n-form-item>
          <n-form-item label="分类名称" path="name">
            <n-input v-model:value="formData.name" placeholder="请输入分类名称" size="large" />
          </n-form-item>
          <n-form-item label="排序值" path="sort_order">
            <n-input-number v-model:value="formData.sort_order" :min="0" size="large" style="width: 100%" />
          </n-form-item>
          <n-form-item label="封面图片">
            <n-upload
              :custom-request="handleUpload"
              :max="1"
              list-type="image-card"
              @finish="handleUploadFinish"
              @remove="handleRemove"
              :default-file-list="fileList"
            >
              点击上传
            </n-upload>
          </n-form-item>
          <n-form-item label="描述" path="description">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              placeholder="请输入描述"
              size="large"
            />
          </n-form-item>
          
          <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
            <n-button size="large" @click="showModal = false">取消</n-button>
            <n-button type="primary" size="large" :loading="submitting" @click="handleSubmit">确定</n-button>
          </div>
        </n-form>
      </n-card>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, h, onMounted, reactive } from 'vue'
import { 
  NButton, 
  useMessage, 
  useDialog,
  NCard,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NUpload,
  NSpin,
  NEmpty,
  NTag,
  NIcon
} from 'naive-ui'
import { Add } from '@vicons/ionicons5'
import { getWorkflowCategories, createWorkflowCategory, updateWorkflowCategory, deleteWorkflowCategory } from '@/api/workflows'
import { uploadFile } from '@/api/common'
import CategoryItem from './CategoryItem.vue'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const categoryData = ref([])
const showModal = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const modalTitle = ref('添加分类')
const fileList = ref([])

const formData = reactive({
  id: null,
  name: '',
  parent: null,
  parentName: '',
  sort_order: 0,
  image: '',
  description: ''
})

const rules = {
  name: { required: true, message: '请输入分类名称', trigger: 'blur' }
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await getWorkflowCategories()
    categoryData.value = res.data || res
  } catch (error) {
    message.error(error.message || '获取分类失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.parent = null
  formData.parentName = ''
  formData.sort_order = 0
  formData.image = ''
  formData.description = ''
  fileList.value = []
}

const handleAdd = (parent) => {
  resetForm()
  if (parent) {
    modalTitle.value = '添加子分类'
    formData.parent = parent.id
    formData.parentName = parent.name
  } else {
    modalTitle.value = '添加一级分类'
  }
  showModal.value = true
}

const findCategoryName = (id, list) => {
  for (const item of list) {
    if (item.id === id) return item.name
    if (item.children) {
      const found = findCategoryName(id, item.children)
      if (found) return found
    }
  }
  return ''
}

const handleEdit = (row) => {
  resetForm()
  modalTitle.value = '编辑分类'
  Object.assign(formData, row)
  // 映射后端返回的 cover 到前端使用的 image
  if (row.cover) {
    formData.image = row.cover
    fileList.value = [{
      id: 'cover',
      name: '封面图',
      status: 'finished',
      url: row.cover
    }]
  }
  
  if (row.parent) {
    formData.parentName = findCategoryName(row.parent, categoryData.value)
  }
  showModal.value = true
}

const handleDelete = (row) => {
  dialog.warning({
    title: '警告',
    content: '确定要删除该分类吗？如果有子分类也会被删除。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteWorkflowCategory(row.id)
        message.success('删除成功')
        fetchCategories()
      } catch (error) {
        message.error(error.message || '删除失败')
      }
    }
  })
}

const handleUpload = async ({ file, onFinish, onError }) => {
  const url = URL.createObjectURL(file.file)
  formData.image = url // 用于预览
  fileList.value = [{
    id: file.id,
    name: file.name,
    status: 'finished',
    url: url,
    file: file.file // 保存原始文件对象
  }]
  onFinish()
}

const handleUploadFinish = ({ file }) => {
  return file
}

const handleRemove = () => {
  formData.image = ''
  fileList.value = []
}

const handleSubmit = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      submitting.value = true
      try {
        // 1. 如果有新选择的文件（在 fileList 中且有 file 对象），先上传
        let coverUrl = formData.image
        if (fileList.value.length > 0 && fileList.value[0].file) {
           try {
             const fileObj = fileList.value[0].file
             const data = new FormData()
             data.append('file', fileObj)
             const res = await uploadFile(data, 'workflow_category_cover')
             coverUrl = res.url // 更新为真实 URL
           } catch (e) {
             message.error('图片上传失败')
             submitting.value = false
             return
           }
        }
        
        // 构造提交数据
        const submitData = { ...formData, cover: coverUrl }
        delete submitData.image

        if (formData.id) {
          await updateWorkflowCategory(formData.id, submitData)
        } else {
          await createWorkflowCategory(submitData)
        }
        
        message.success(formData.id ? '更新成功' : '创建成功')
        showModal.value = false
        fetchCategories()
      } catch (error) {
        message.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.category-tree-container {
    border-radius: 4px;
}

.category-modal {
    width: 600px;
}

.auth-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 24px;
  color: #333;
  font-weight: 700;
  margin-bottom: 8px;
}

.empty-state {
    padding: 40px 0;
}
</style>
