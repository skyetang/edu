<template>
  <div class="workflow-list">
    <n-card title="工作流管理">
      <template #header-extra>
        <n-button type="primary" @click="handleAdd">
          添加工作流
        </n-button>
      </template>

      <div class="search-bar">
        <n-input v-model:value="searchQuery" placeholder="搜索工作流名称" clearable @keyup.enter="handleSearch" style="width: 300px" />
        <n-select v-model:value="searchStatus" :options="statusOptions" placeholder="状态" clearable style="width: 150px" />
        <n-button type="primary" ghost @click="handleSearch">搜索</n-button>
      </div>

      <n-data-table
        remote
        :columns="columns"
        :data="workflowData"
        :loading="loading"
        :pagination="pagination"
        :row-key="row => row.id"
        @update:page="handlePageChange"
      />
    </n-card>

    <!-- 添加/编辑工作流弹窗 -->
    <n-modal v-model:show="showModal">
      <n-card
        class="auth-card workflow-modal"
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
          <n-form-item label="工作流名称" path="title">
            <n-input v-model:value="formData.title" placeholder="请输入工作流名称" size="large" />
          </n-form-item>

          <n-form-item label="分类" path="category">
            <n-cascader
              v-model:value="formData.category"
              :options="categoryOptions"
              label-field="name"
              value-field="id"
              placeholder="请选择分类"
              size="large"
              check-strategy="child"
            />
          </n-form-item>

          <n-form-item label="描述" path="description">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              placeholder="请输入描述"
              size="large"
              :autosize="{ minRows: 2, maxRows: 4 }"
            />
          </n-form-item>

          <n-grid :cols="2" :x-gap="24">
            <n-form-item-grid-item label="开始节点">
              <n-input 
                v-model:value="formData.start_node" 
                type="textarea"
                placeholder="请输入开始节点" 
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item-grid-item>
            <n-form-item-grid-item label="结束节点">
              <n-input 
                v-model:value="formData.end_node" 
                type="textarea"
                placeholder="请输入结束节点" 
                :autosize="{ minRows: 2, maxRows: 4 }"
              />
            </n-form-item-grid-item>
          </n-grid>

          <n-form-item label="节点详情">
             <n-input
              v-model:value="formData.node_details"
              type="textarea"
              placeholder="JSON 或文本描述"
              :autosize="{ minRows: 3, maxRows: 6 }"
            />
          </n-form-item>

          <n-grid :cols="2" :x-gap="24">
            <n-form-item-grid-item label="封面图片">
              <div class="upload-wrapper">
                <n-upload
                  :custom-request="handleCoverUpload"
                  :max="1"
                  list-type="image-card"
                  @finish="handleCoverFinish"
                  @remove="handleCoverRemove"
                  :default-file-list="coverFileList"
                >
                  点击上传
                </n-upload>
              </div>
            </n-form-item-grid-item>
            <n-form-item-grid-item label="演示视频">
              <div class="upload-wrapper">
                <div v-if="videoPreviewUrl" class="video-upload-card filled">
                  <video :src="videoPreviewUrl" controls class="video-preview"></video>
                  <div class="video-card-actions">
                    <n-button circle type="error" size="small" @click="handleVideoRemove">
                      <template #icon><n-icon><TrashOutline /></n-icon></template>
                    </n-button>
                  </div>
                </div>
                
                 <n-upload
                  v-else
                  :custom-request="handleVideoUpload"
                  :max="1"
                  @finish="handleVideoFinish"
                  @remove="handleVideoRemove"
                  :default-file-list="videoFileList"
                  accept="video/*"
                  :show-file-list="false"
                >
                   <div class="video-upload-card empty">
                    <n-icon size="30" color="#999"><CloudUploadOutline /></n-icon>
                    <span class="upload-text">点击上传视频</span>
                  </div>
                </n-upload>
              </div>
            </n-form-item-grid-item>
          </n-grid>

          <n-form-item label="标签">
            <n-input v-model:value="formData.tags" placeholder="多个标签用逗号分隔" />
          </n-form-item>

          <n-grid :cols="3" :x-gap="24">
            <n-form-item-grid-item label="访问权限">
               <n-select v-model:value="formData.access_level" :options="accessLevelOptions" placeholder="请选择访问权限" />
            </n-form-item-grid-item>
            <n-form-item-grid-item label="排序值">
               <n-input-number v-model:value="formData.sort_order" :min="0" style="width: 100%" />
            </n-form-item-grid-item>
            <n-form-item-grid-item label="状态">
               <n-select v-model:value="formData.status" :options="statusOptions" />
            </n-form-item-grid-item>
          </n-grid>

          <n-form-item label="附件">
            <div style="width: 100%">
              <div v-if="attachmentFileList.length" class="file-upload-card filled">
                 <div class="file-info">
                   <n-icon size="24" color="#2080f0"><AttachOutline /></n-icon>
                   <span class="file-name">{{ attachmentFileList[0].name }}</span>
                 </div>
                 <div class="file-actions">
                   <n-button text type="error" size="small" @click="handleAttachmentRemove">
                      <template #icon><n-icon><TrashOutline /></n-icon></template>
                      删除
                   </n-button>
                 </div>
              </div>
              <n-upload
                v-else
                :custom-request="handleAttachmentUpload"
                :max="1"
                @finish="handleAttachmentFinish"
                @remove="handleAttachmentRemove"
                :default-file-list="attachmentFileList"
                :show-file-list="false"
              >
                <div class="file-upload-card empty">
                  <n-icon size="24" color="#999"><CloudUploadOutline /></n-icon>
                  <span class="upload-text">点击上传附件</span>
                </div>
              </n-upload>
            </div>
          </n-form-item>

          <n-form-item label="参考资料">
             <n-input
              v-model:value="formData.reference"
              placeholder="参考链接或文本"
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
import { ref, h, onMounted, reactive, watch } from 'vue'
import { 
  NButton, 
  useMessage, 
  useDialog,
  NCard,
  NModal,
  NForm,
  NFormItem,
  NFormItemGridItem,
  NInput,
  NInputNumber,
  NUpload,
  NSpin,
  NEmpty,
  NDataTable,
  NSpace,
  NTag,
  NSelect,
  NCascader,
  NGrid,
  NIcon
} from 'naive-ui'
import { AttachOutline, TrashOutline, CloudUploadOutline } from '@vicons/ionicons5'
import { getWorkflows, createWorkflow, updateWorkflow, deleteWorkflow, getWorkflowCategories } from '@/api/workflows'
import { getPlans } from '@/api/membership'
import { uploadFile } from '@/api/common'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const workflowData = ref([])
const showModal = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const modalTitle = ref('添加工作流')

// Search
const searchQuery = ref('')
const searchStatus = ref(null)

const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  prefix: ({ itemCount }) => `共 ${itemCount} 条`
})

// Options
const categoryOptions = ref([])
const accessLevelOptions = ref([])
const statusOptions = [
  { label: '草稿', value: 'DRAFT' },
  { label: '发布', value: 'PUBLISHED' }
]

// Files
const coverFileList = ref([])
const videoFileList = ref([])
const attachmentFileList = ref([])
const videoPreviewUrl = ref('')
const attachmentUrl = ref('')

const formData = reactive({
  id: null,
  title: '',
  category: null,
  description: '',
  start_node: '',
  end_node: '',
  node_details: '',
  cover: '',
  video_url: '',
  attachment: '',
  reference: '',
  tags: '',
  sort_order: 0,
  status: 'DRAFT',
  access_level: 0
})

const rules = {
  title: { required: true, message: '请输入工作流名称', trigger: 'blur' },
  category: { required: true, type: 'number', message: '请选择分类', trigger: 'change' }
}

// Columns
const columns = [
  { title: 'ID', key: 'id', width: 60 },
  { 
    title: '封面', 
    key: 'cover',
    width: 80,
    render(row) {
      return row.cover ? h('img', { src: row.cover, style: 'height: 40px; border-radius: 4px' }) : '-'
    }
  },
  { title: '名称', key: 'title', width: 150 },
  { title: '分类', key: 'category_name', width: 120 },
  { 
    title: '状态', 
    key: 'status',
    width: 80,
    render(row) {
      return row.status === 'PUBLISHED' 
        ? h(NTag, { type: 'success', size: 'small', bordered: false }, { default: () => '已发布' })
        : h(NTag, { type: 'warning', size: 'small', bordered: false }, { default: () => '草稿' })
    }
  },
  { title: '排序', key: 'sort_order', width: 70 },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', type: 'primary', ghost: true, onClick: () => handleEdit(row) }, { default: () => '编辑' }),
          h(NButton, { size: 'small', type: 'error', ghost: true, onClick: () => handleDelete(row) }, { default: () => '删除' })
        ]
      })
    }
  }
]

// Fetch Data
const fetchWorkflows = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: searchQuery.value,
      status: searchStatus.value
    }
    const res = await getWorkflows(params)
    workflowData.value = res.data || res.results || []
    if (res.meta && res.meta.pagination) {
        pagination.itemCount = res.meta.pagination.total
    } else if (res.count) {
        pagination.itemCount = res.count
    }
  } catch (error) {
    message.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await getWorkflowCategories()
    const list = res.data || res
    
    // Process recursive categories: remove empty children to make them selectable leaves
    const processCategories = (categories) => {
      if (!Array.isArray(categories)) return []
      return categories.map(cat => {
        const newCat = { ...cat }
        if (newCat.children && newCat.children.length > 0) {
          newCat.children = processCategories(newCat.children)
        } else {
          delete newCat.children
        }
        return newCat
      })
    }

    categoryOptions.value = processCategories(list)
  } catch (e) {
    console.error(e)
  }
}

const fetchAccessLevels = async () => {
  try {
    const options = [{ label: '免费', value: 0 }]
    const res = await getPlans()
    const plans = res.data || res || []
    if (Array.isArray(plans)) {
      plans.forEach(p => {
        if (p.level > 0) {
          options.push({ label: p.name, value: p.level })
        }
      })
    }
    accessLevelOptions.value = options
  } catch (e) {
    console.error(e)
    accessLevelOptions.value = [
      { label: '免费', value: 0 },
      { label: 'VIP', value: 1 }
    ]
  }
}

// Handlers
const handleSearch = () => {
  pagination.page = 1
  fetchWorkflows()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchWorkflows()
}

const resetForm = () => {
  Object.assign(formData, {
    id: null,
    title: '',
    category: null,
    description: '',
    start_node: '',
    end_node: '',
    node_details: '',
    cover: '',
    video_url: '',
    attachment: '',
    reference: '',
    tags: '',
    sort_order: 0,
    status: 'DRAFT',
    access_level: 0
  })
  coverFileList.value = []
  videoFileList.value = []
  attachmentFileList.value = []
  videoPreviewUrl.value = ''
  attachmentUrl.value = ''
}

const handleAdd = () => {
  resetForm()
  modalTitle.value = '添加工作流'
  showModal.value = true
}

const handleEdit = (row) => {
  resetForm()
  modalTitle.value = '编辑工作流'
  Object.assign(formData, row)
  
  // Files pre-population
  if (row.cover) {
    coverFileList.value = [{ id: 'cover', name: '封面', status: 'finished', url: row.cover }]
  }
  if (row.video_url) {
    videoFileList.value = [{ id: 'video', name: '视频', status: 'finished', url: row.video_url }]
    videoPreviewUrl.value = row.video_url
  }
  if (row.attachment) {
    const fileName = row.attachment.split('/').pop() || '附件'
    attachmentFileList.value = [{ id: 'att', name: fileName, status: 'finished', url: row.attachment }]
    attachmentUrl.value = row.attachment
  }
  
  showModal.value = true
}

const handleDelete = (row) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除该工作流吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteWorkflow(row.id)
        message.success('删除成功')
        fetchWorkflows()
      } catch (e) {
        message.error('删除失败')
      }
    }
  })
}

// Upload Handlers
const createUploadHandler = (field, listRef, type='image') => {
  return async ({ file, onFinish, onError }) => {
    const url = URL.createObjectURL(file.file)
    listRef.value = [{
        id: file.id,
        name: file.name,
        status: 'finished',
        url: url,
        file: file.file
    }]
    
    // Set preview for video
    if (field === 'video_url') {
      videoPreviewUrl.value = url
    }
    
    onFinish()
  }
}

const handleCoverUpload = createUploadHandler('cover', coverFileList)
const handleVideoUpload = createUploadHandler('video_url', videoFileList, 'video')
const handleAttachmentUpload = createUploadHandler('attachment', attachmentFileList, 'file')

const handleCoverRemove = () => { coverFileList.value = []; formData.cover = '' }
const handleVideoRemove = () => { videoFileList.value = []; formData.video_url = ''; videoPreviewUrl.value = '' }
const handleAttachmentRemove = () => { attachmentFileList.value = []; formData.attachment = ''; attachmentUrl.value = '' }

const handleCoverFinish = ({file}) => file
const handleVideoFinish = ({file}) => file
const handleAttachmentFinish = ({file}) => file


const processFileUpload = async (fileListRef, prefix) => {
    if (fileListRef.value.length > 0 && fileListRef.value[0].file) {
        try {
            const data = new FormData()
            data.append('file', fileListRef.value[0].file)
            const res = await uploadFile(data, prefix)
            return res.url
        } catch (e) {
            throw new Error('上传失败')
        }
    }
    return null
}

const handleSubmit = async () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      submitting.value = true
      try {
        // Upload files if new ones exist
        if (coverFileList.value.length > 0 && coverFileList.value[0].file) {
             const url = await processFileUpload(coverFileList, 'workflow_cover')
             formData.cover = url
        }
        
        if (videoFileList.value.length > 0 && videoFileList.value[0].file) {
             const url = await processFileUpload(videoFileList, 'workflow_video')
             formData.video_url = url
        }
        
        if (attachmentFileList.value.length > 0 && attachmentFileList.value[0].file) {
             const url = await processFileUpload(attachmentFileList, 'workflow_attachment')
             formData.attachment = url
        }

        if (formData.id) {
          await updateWorkflow(formData.id, formData)
        } else {
          await createWorkflow(formData)
        }
        message.success('保存成功')
        showModal.value = false
        fetchWorkflows()
      } catch (e) {
        message.error(e.message || '保存失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchWorkflows()
  fetchCategories()
  fetchAccessLevels()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.workflow-modal {
    width: 800px;
    max-width: 90vw;
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

.upload-wrapper {
  width: 100%;
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.attachment-link {
  margin-top: 8px;
}

.download-link {
  color: #2080f0;
  text-decoration: none;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
}

.download-link:hover {
  text-decoration: underline;
}

.video-upload-card {
  width: 160px; /* 4:3 ratio based on height */
  height: 120px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.3s;
  position: relative;
  overflow: hidden;
  gap: 8px;
}

.video-upload-card.empty {
  border: 1px dashed rgb(224, 224, 230);
  background-color: rgba(0, 0, 0, 0.02);
}

.video-upload-card.empty:hover {
  border-color: #18a058;
}

.video-upload-card.filled {
  border: 1px solid rgb(239, 239, 245);
  background-color: #000;
}

.video-card-actions {
  position: absolute;
  top: 4px;
  right: 4px;
  display: none;
}

.video-upload-card.filled:hover .video-card-actions {
  display: block;
}

.upload-text {
  color: #666;
  font-size: 12px;
}

/* Override Naive UI Upload Styles to match */
:deep(.n-upload-trigger.n-upload-trigger--image-card),
:deep(.n-upload-file-list .n-upload-file.n-upload-file--image-card-type) {
  width: 160px !important;
}

.file-upload-card {
  width: 100%;
  height: 48px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  box-sizing: border-box;
  transition: all 0.3s;
}

.file-upload-card.empty {
  border: 1px dashed rgb(224, 224, 230);
  background-color: rgba(0, 0, 0, 0.02);
  justify-content: center;
  cursor: pointer;
  gap: 8px;
}

.file-upload-card.empty:hover {
  border-color: #18a058;
  background-color: rgba(0, 0, 0, 0.05);
}

.file-upload-card.filled {
  border: 1px solid rgb(239, 239, 245);
  background-color: #fff;
  justify-content: space-between;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow: hidden;
}

.file-name {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-download-btn {
  color: #2080f0;
  font-size: 13px;
  text-decoration: none;
  cursor: pointer;
}

.file-download-btn:hover {
  text-decoration: underline;
}
</style>