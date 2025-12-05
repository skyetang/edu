<template>
  <div class="course-list">
    <n-card title="课程管理">
      <template #header-extra>
        <n-button type="primary" @click="handleAdd">
          添加课程
        </n-button>
      </template>

      <n-data-table
        :columns="columns"
        :data="courseData"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
      />
    </n-card>

    <!-- 添加/编辑课程弹窗 -->
    <n-modal v-model:show="showModal">
      <n-card
        class="auth-card course-modal"
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
          <n-form-item label="课程名称" path="title">
            <n-input v-model:value="formData.title" placeholder="请输入课程名称" size="large" />
          </n-form-item>
          <n-form-item label="所属分类" path="category">
            <n-cascader
              v-model:value="formData.category"
              :options="categoryOptions"
              key-field="id"
              label-field="name"
              value-field="id"
              children-field="children"
              placeholder="请选择分类"
              check-strategy="child"
              :show-path="false"
              size="large"
            />
          </n-form-item>
          <n-form-item label="课程封面">
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
          <n-form-item label="课程描述">
            <n-input
              v-model:value="formData.description"
              type="textarea"
              placeholder="请输入课程描述"
              size="large"
            />
          </n-form-item>
          <n-form-item label="讲师" path="instructor">
            <n-input v-model:value="formData.instructor" placeholder="请输入讲师姓名" size="large" />
          </n-form-item>
          <n-form-item label="排序" path="sort_order">
            <n-input-number v-model:value="formData.sort_order" :min="0" size="large" style="width: 100%" />
          </n-form-item>
          <n-form-item label="访问权限">
            <n-select
              v-model:value="formData.access_level"
              :options="accessLevelOptions"
              size="large"
            />
          </n-form-item>
          <n-form-item label="是否发布">
            <n-switch v-model:value="formData.is_published" size="large" />
          </n-form-item>
          <n-form-item label="课程状态">
            <n-radio-group v-model:value="formData.status" size="large">
              <n-space>
                <n-radio value="UPDATING">更新中</n-radio>
                <n-radio value="FINISHED">已完结</n-radio>
              </n-space>
            </n-radio-group>
          </n-form-item>
          
          <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
            <n-button size="large" @click="showModal = false">取消</n-button>
            <n-button type="primary" size="large" :loading="submitting" @click="handleSubmit">确定</n-button>
          </div>
        </n-form>
      </n-card>
    </n-modal>

    <!-- 章节管理弹窗 -->
    <ChapterManager
      v-model:show="showChapterModal"
      :course-id="currentCourseId"
      :course-title="currentCourseTitle"
    />
  </div>
</template>

<script setup>
import { ref, h, onMounted, reactive } from 'vue'
import { 
  NButton, 
  NSpace, 
  NTag, 
  useMessage, 
  useDialog,
  NCard,
  NDataTable,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NTreeSelect,
  NCascader,
  NUpload,
  NInputNumber,
  NSelect,
  NSwitch,
  NRadioGroup,
  NRadio
} from 'naive-ui'
import { getCourses, createCourse, updateCourse, deleteCourse, getCategories } from '@/api/courses'
import { uploadFile } from '@/api/common'
import ChapterManager from './ChapterManager.vue'

import { getPlans } from '@/api/membership'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const courseData = ref([])
const showModal = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const modalTitle = ref('添加课程')
const fileList = ref([])
const categoryOptions = ref([])
const accessLevelOptions = ref([])

// 章节管理相关
const showChapterModal = ref(false)
const currentCourseId = ref(null)
const currentCourseTitle = ref('')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0
})

const formData = reactive({
  id: null,
  title: '',
  category: null,
  cover: '',
  description: '',
  instructor: '',
  sort_order: 0,
  access_level: 0,
  is_published: false,
  status: 'UPDATING'
})

const rules = {
  title: { required: true, message: '请输入课程名称', trigger: 'blur' },
  category: { required: true, type: 'number', message: '请选择分类', trigger: 'change' },
  instructor: { required: true, message: '请输入讲师姓名', trigger: 'blur' }
}

const columns = [
  { title: '课程名称', key: 'title' },
  { title: '所属分类', key: 'category_name' }, // 需要后端返回category_name或前端匹配
  { 
    title: '封面', 
    key: 'cover',
    render(row) {
      if (row.cover) {
        return h('img', { src: row.cover, style: 'height: 40px; border-radius: 4px;' })
      }
      return '-'
    }
  },
  { title: '讲师', key: 'instructor' },
  { 
    title: '访问权限', 
    key: 'access_level',
    render(row) {
      // accessLevelOptions.value 因为是 ref，所以需要 .value
      const label = accessLevelOptions.value.find(o => o.value === row.access_level)?.label || row.access_level
      return h(NTag, { type: 'info', bordered: false }, { default: () => label })
    }
  },
  { 
    title: '发布状态', 
    key: 'is_published',
    render(row) {
      return row.is_published 
        ? h(NTag, { type: 'success', bordered: false }, { default: () => '已发布' })
        : h(NTag, { type: 'default', bordered: false }, { default: () => '未发布' })
    }
  },
  { 
    title: '状态', 
    key: 'status',
    render(row) {
      return row.status === 'FINISHED' 
        ? h(NTag, { type: 'success', bordered: false }, { default: () => '已完结' })
        : h(NTag, { type: 'warning', bordered: false }, { default: () => '更新中' })
    }
  },
  {
    title: '操作',
    key: 'actions',
    width: 300,
    render(row) {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, { size: 'small', type: 'info', onClick: () => handleChapters(row) }, { default: () => '查看章节' }),
          h(NButton, { size: 'small', type: 'primary', onClick: () => handleEdit(row) }, { default: () => '编辑' }),
          h(NButton, { size: 'small', type: 'error', onClick: () => handleDelete(row) }, { default: () => '删除' })
        ]
      })
    }
  }
]

const fetchCategoriesData = async () => {
  try {
    const res = await getCategories()
    // 过滤掉第三级分类，只保留一级和二级
    const filterCategories = (categories, depth = 1) => {
      return categories.map(cat => {
        const newCat = { ...cat }
        
        // 如果深度为2，则移除 children（不再显示第三级）
        if (depth >= 2) {
          delete newCat.children
          return newCat
        }
        
        // 否则递归处理子节点
        if (newCat.children && newCat.children.length > 0) {
          newCat.children = filterCategories(newCat.children, depth + 1)
        } else {
          // 如果没有子节点，移除 children 属性，使其成为叶子节点
          delete newCat.children
        }
        
        return newCat
      })
    }
    categoryOptions.value = filterCategories(res)
  } catch (error) {
    // ignore or log
  }
}

const fetchAccessLevels = async () => {
  try {
    // 默认包含 "所有用户"
    const options = [{ label: '所有用户', value: 0 }]
    
    const res = await getPlans()
    // 假设 res 是 Plan 数组，根据业务逻辑，通常 access_level 对应 plan 的 level 字段
    // 如果后端返回的是带 level 的对象，这里进行映射
    // 如果 getPlans 返回的是 { results: [...] } 结构，需要适配
    const plans = Array.isArray(res) ? res : (res.results || [])
    
    plans.forEach(plan => {
        // 假设 Plan 模型有 name 和 level 字段
        // 如果没有 level，可能需要使用 id，但这取决于后端权限判断逻辑
        // 这里假设后端通过 level 判断权限大小
        if (plan.level > 0) {
          options.push({ 
            label: plan.name, 
            value: plan.level 
          })
        }
      })
    
    // 去重并排序 (可选)
    accessLevelOptions.value = options
  } catch (error) {
    console.error('Fetch plans failed:', error)
    // Fallback default options
    accessLevelOptions.value = [
      { label: '所有用户', value: 0 },
      { label: 'VIP会员', value: 1 }
    ]
  }
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const res = await getCourses({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    
    // 适配新的响应结构 { data: [], meta: { pagination: { total, ... } } }
    if (res.data && res.meta) {
      courseData.value = res.data
      pagination.itemCount = res.meta.pagination.total
    } else if (Array.isArray(res)) {
      // 兼容直接返回数组的情况
      courseData.value = res
      pagination.itemCount = res.length
    } else if (res.results) {
       // 兼容旧的 DRF 分页格式
       courseData.value = res.results
       pagination.itemCount = res.count
    } else {
       courseData.value = []
       pagination.itemCount = 0
    }
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchCourses()
}

const resetForm = () => {
  formData.id = null
  formData.title = ''
  formData.category = null
  formData.cover = ''
  formData.description = ''
  formData.instructor = ''
  formData.sort_order = 0
  formData.access_level = 0
  formData.is_published = false
  formData.status = 'UPDATING'
  fileList.value = []
}

const handleAdd = () => {
  resetForm()
  modalTitle.value = '添加课程'
  showModal.value = true
}

const handleEdit = (row) => {
  resetForm()
  modalTitle.value = '编辑课程'
  Object.assign(formData, row)
  if (row.cover) {
    fileList.value = [{
      id: 'cover',
      name: '封面图',
      status: 'finished',
      url: row.cover
    }]
  }
  showModal.value = true
}

const handleChapters = (row) => {
  currentCourseId.value = row.id
  currentCourseTitle.value = row.title
  showChapterModal.value = true
}

const handleDelete = (row) => {
  dialog.warning({
    title: '警告',
    content: '确定要删除该课程吗？相关的章节和课时也会被删除。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteCourse(row.id)
        message.success('删除成功')
        fetchCourses()
      } catch (error) {
        // error handled
      }
    }
  })
}

const handleUpload = async ({ file, onFinish, onError }) => {
  // 暂存文件用于提交时上传
  const url = URL.createObjectURL(file.file)
  formData.cover = url // 预览
  fileList.value = [{
    id: file.id,
    name: file.name,
    status: 'finished',
    url: url,
    file: file.file
  }]
  onFinish()
}

const handleUploadFinish = () => {
  // message.success('上传成功')
}

const handleRemove = () => {
  formData.cover = ''
  fileList.value = []
}

const handleSubmit = () => {
  formRef.value?.validate(async (errors) => {
    if (!errors) {
      submitting.value = true
      try {
        // 1. 如果有新文件，先上传
        if (fileList.value.length > 0 && fileList.value[0].file) {
          try {
             const fileObj = fileList.value[0].file
             const data = new FormData()
             data.append('file', fileObj)
             const res = await uploadFile(data, 'course_cover')
             formData.cover = res.url // 更新为真实 URL
          } catch (e) {
             message.error('图片上传失败')
             submitting.value = false
             return
          }
        }

        if (formData.id) {
          await updateCourse(formData.id, formData)
          message.success('更新成功')
        } else {
          await createCourse(formData)
          message.success('创建成功')
        }
        showModal.value = false
        fetchCourses()
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  fetchCategoriesData()
  fetchAccessLevels()
  fetchCourses()
})
</script>

<style scoped>
.auth-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.course-modal {
  width: 700px;
}

.auth-header {
  text-align: center;
}

.modal-title {
  font-size: 24px;
  color: #333;
  font-weight: 700;
  margin-bottom: 8px;
}
</style>
