<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
  >
    <n-card
      class="auth-card chapter-modal"
      :bordered="false"
      size="large"
      role="dialog"
      aria-modal="true"
      closable
      @close="$emit('update:show', false)"
    >
      <template #header>
        <div class="modal-title">章节管理 - {{ courseTitle }}</div>
      </template>
      
      <div class="chapter-manager-content">
        <n-spin :show="loading">
          <div v-if="chapters.length === 0" class="empty-state">
            <n-empty description="暂无章节，请添加" />
          </div>
          
          <n-collapse v-else default-expanded-names="" class="chapter-list-container">
            <n-collapse-item
              v-for="chapter in chapters"
              :key="chapter.id"
              :name="chapter.id"
            >
              <template #header>
                <div class="chapter-header">
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <span class="chapter-desc" v-if="chapter.description">({{ chapter.description }})</span>
                </div>
              </template>
              <template #header-extra>
                <n-space>
                  <n-button size="tiny" type="primary" ghost @click.stop="handleAddLesson(chapter)">上传课时</n-button>
                  <n-button size="tiny" @click.stop="handleEditChapter(chapter)">编辑</n-button>
                  <n-button size="tiny" type="error" @click.stop="handleDeleteChapter(chapter)">删除</n-button>
                </n-space>
              </template>

              <div class="lesson-list">
                <div v-if="chapter.lessons && chapter.lessons.length > 0">
                  <n-list>
                    <n-list-item v-for="lesson in chapter.lessons" :key="lesson.id">
                      <div class="lesson-item">
                        <div class="lesson-info">
                          <div class="lesson-title">{{ lesson.title }}</div>
                          <div class="lesson-meta">
                            <span>时长: {{ lesson.duration || '00:00' }}</span>
                            <span>分辨率: {{ lesson.resolution || '未知' }}</span>
                          </div>
                        </div>
                        <div class="lesson-actions">
                          <n-button size="tiny" text type="primary" @click="handleEditLesson(chapter, lesson)">编辑</n-button>
                          <n-button size="tiny" text type="error" @click="handleDeleteLesson(lesson)">删除</n-button>
                        </div>
                      </div>
                    </n-list-item>
                  </n-list>
                </div>
                <n-empty v-else description="暂无课时" />
              </div>
            </n-collapse-item>
          </n-collapse>
        </n-spin>
      </div>

      <div class="chapter-footer">
        <n-button type="primary" size="large" @click="handleAddChapter">添加章节</n-button>
      </div>
    </n-card>
  </n-modal>

  <!-- 添加/编辑章节弹窗 -->
  <n-modal v-model:show="showChapterForm">
    <n-card
      class="auth-card chapter-form-modal"
      :bordered="false"
      size="large"
      role="dialog"
      aria-modal="true"
      closable
      @close="showChapterForm = false"
    >
      <template #header>
        <div class="modal-title">{{ chapterModalTitle }}</div>
      </template>
      <n-form :model="chapterForm" label-placement="left" label-width="80">
        <n-form-item label="章节名称">
          <n-input v-model:value="chapterForm.title" placeholder="请输入章节名称" size="large" />
        </n-form-item>
        <n-form-item label="描述">
          <n-input v-model:value="chapterForm.description" type="textarea" placeholder="请输入描述" size="large" />
        </n-form-item>
        <n-form-item label="排序">
          <n-input-number v-model:value="chapterForm.sort_order" :min="0" size="large" style="width: 100%" />
        </n-form-item>
        
        <div class="dialog-footer">
          <n-button size="large" @click="showChapterForm = false">取消</n-button>
          <n-button type="primary" size="large" :loading="chapterSubmitting" @click="submitChapter">确定</n-button>
        </div>
      </n-form>
    </n-card>
  </n-modal>

  <!-- 添加/编辑课时弹窗 -->
  <n-modal v-model:show="showLessonForm">
    <n-card
      class="auth-card lesson-form-modal"
      :bordered="false"
      size="large"
      role="dialog"
      aria-modal="true"
      closable
      @close="showLessonForm = false"
    >
      <template #header>
        <div class="modal-title">{{ lessonModalTitle }}</div>
      </template>
      <n-form :model="lessonForm" label-placement="left" label-width="80">
        <n-form-item label="所属章节">
          <n-input :value="currentChapter?.title" disabled size="large" />
        </n-form-item>
        <n-form-item label="课时标题">
          <n-input v-model:value="lessonForm.title" placeholder="请输入课时标题" size="large" />
        </n-form-item>
        <n-form-item label="课时描述">
          <n-input v-model:value="lessonForm.description" type="textarea" placeholder="请输入描述" size="large" />
        </n-form-item>
        
        <!-- 视频上传 -->
        <n-form-item label="视频文件">
          <div style="width: 100%">
            <div v-if="!uploadingVideo">
              <!-- 视频预览/已上传状态 -->
              <div v-if="videoPreviewUrl" class="video-upload-card filled">
                <video :src="videoPreviewUrl" controls class="video-preview"></video>
                <div class="video-card-actions">
                  <n-button circle type="error" size="small" @click="handleRemoveVideo">
                    <template #icon><n-icon><TrashOutline /></n-icon></template>
                  </n-button>
                </div>
              </div>
              
              <!-- 视频上传按钮 -->
              <n-upload
                v-else
                ref="uploadRef"
                :default-upload="false"
                :max="1"
                accept="video/*"
                :show-file-list="false"
                @change="handleFileChange"
              >
                <div class="video-upload-card empty">
                  <n-icon size="30" color="#999"><CloudUploadOutline /></n-icon>
                  <span class="upload-text">点击上传视频</span>
                </div>
              </n-upload>
            </div>

            <!-- 进度条 -->
            <div v-if="uploadingVideo && videoProgress > 0" class="progress-wrapper">
              <div class="progress-label">视频上传进度</div>
              <n-progress type="line" :percentage="videoProgress" indicator-placement="inside" processing />
            </div>
          </div>
        </n-form-item>

        <!-- 封面上传 -->
        <n-form-item label="视频封面">
          <div style="width: 100%">
            <n-upload
              ref="coverUploadRef"
              :default-upload="false"
              :max="1"
              list-type="image-card"
              accept="image/*"
              :default-file-list="coverFileList"
              @change="handleCoverChange"
            >
              点击上传
            </n-upload>
            
            <div v-if="uploadingVideo && coverProgress > 0" class="progress-wrapper">
              <div class="progress-label">封面上传进度</div>
              <n-progress type="line" :percentage="coverProgress" indicator-placement="inside" processing />
            </div>
          </div>
        </n-form-item>

        <n-form-item label="排序">
          <n-input-number v-model:value="lessonForm.sort_order" :min="0" size="large" style="width: 100%" />
        </n-form-item>
        
        <div class="dialog-footer">
          <n-button size="large" @click="showLessonForm = false">取消</n-button>
          <n-button type="primary" size="large" :loading="lessonSubmitting" @click="submitLesson" :disabled="uploadingVideo">确定</n-button>
        </div>
      </n-form>
    </n-card>
  </n-modal>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { 
  useMessage, 
  useDialog,
  NModal,
  NSpin,
  NEmpty,
  NCollapse,
  NCollapseItem,
  NButton,
  NSpace,
  NList,
  NListItem,
  NTag,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NUpload,
  NProgress,
  NAlert,
  NIcon
} from 'naive-ui'
import { 
  CloudUploadOutline,
  TrashOutline
} from '@vicons/ionicons5'
import { 
  getChapters, 
  createChapter, 
  updateChapter, 
  deleteChapter,
  createLesson,
  updateLesson,
  deleteLesson
} from '@/api/courses'
import { getVodSignature } from '@/api/common'
import { uploadMediaFiles, extractUploadInfo } from '@/utils/upload'

const props = defineProps({
  show: Boolean,
  courseId: Number,
  courseTitle: String
})

const emit = defineEmits(['update:show'])

const message = useMessage()
const dialog = useDialog()
const loading = ref(false)
const chapters = ref([])

// 章节管理
const showChapterForm = ref(false)
const chapterSubmitting = ref(false)
const chapterModalTitle = ref('')
const chapterForm = reactive({
  id: null,
  title: '',
  description: '',
  sort_order: 0
})

// 课时管理
const showLessonForm = ref(false)
const lessonSubmitting = ref(false)
const lessonModalTitle = ref('')
const currentChapter = ref(null)
const lessonForm = reactive({
  id: null,
  title: '',
  description: '',
  sort_order: 0,
  video_file_id: '',
  video_url: '',
  cover: '',
  duration: '',
  resolution: ''
})

// 腾讯云上传相关
const uploadingVideo = ref(false)
const videoProgress = ref(0)
const coverProgress = ref(0)
const selectedVideoFile = ref(null)
const selectedCoverFile = ref(null)
const uploadRef = ref(null)
const coverUploadRef = ref(null)

const coverFileList = ref([])
const videoPreviewUrl = ref('')
const coverPreviewUrl = ref('')

// 获取章节列表
const fetchChapters = async () => {
  if (!props.courseId) return
  loading.value = true
  try {
    const res = await getChapters({ course: props.courseId })
    chapters.value = res
  } catch (error) {
    message.error('获取章节列表失败')
  } finally {
    loading.value = false
  }
}

// 监听显示状态
watch(() => props.show, (val) => {
  if (val) {
    fetchChapters()
  }
})

// --- 章节操作 ---
const handleAddChapter = () => {
  chapterModalTitle.value = '添加章节'
  chapterForm.id = null
  chapterForm.title = ''
  chapterForm.description = ''
  chapterForm.sort_order = 0
  showChapterForm.value = true
}

const handleEditChapter = (chapter) => {
  chapterModalTitle.value = '编辑章节'
  chapterForm.id = chapter.id
  chapterForm.title = chapter.title
  chapterForm.description = chapter.description
  chapterForm.sort_order = chapter.sort_order
  showChapterForm.value = true
}

const handleDeleteChapter = (chapter) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除该章节吗？删除后该章节下的课时也会被删除。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteChapter(chapter.id)
        message.success('删除成功')
        fetchChapters()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

const submitChapter = async () => {
  if (!chapterForm.title) {
    message.warning('请输入章节名称')
    return
  }
  
  chapterSubmitting.value = true
  try {
    const data = {
      course: props.courseId,
      title: chapterForm.title,
      description: chapterForm.description,
      sort_order: chapterForm.sort_order
    }
    
    if (chapterForm.id) {
      await updateChapter(chapterForm.id, data)
      message.success('更新成功')
    } else {
      await createChapter(data)
      message.success('创建成功')
    }
    showChapterForm.value = false
    fetchChapters()
  } catch (error) {
    message.error(chapterForm.id ? '更新失败' : '创建失败')
  } finally {
    chapterSubmitting.value = false
  }
}

// --- 课时操作 ---
const handleAddLesson = (chapter) => {
  currentChapter.value = chapter
  lessonModalTitle.value = '添加课时'
  resetLessonForm()
  showLessonForm.value = true
}

const handleEditLesson = (chapter, lesson) => {
  currentChapter.value = chapter
  lessonModalTitle.value = '编辑课时'
  lessonForm.id = lesson.id
  lessonForm.title = lesson.title
  lessonForm.description = lesson.description
  lessonForm.sort_order = lesson.sort_order
  lessonForm.video_file_id = lesson.video_file_id
  lessonForm.video_url = lesson.video_url
  lessonForm.cover = lesson.cover
  lessonForm.duration = lesson.duration
  lessonForm.resolution = lesson.resolution
  
  // Reset upload state
  selectedVideoFile.value = null
  selectedCoverFile.value = null
  videoProgress.value = 0
  coverProgress.value = 0
  uploadingVideo.value = false
  
  // Set previews
  videoPreviewUrl.value = lesson.video_url
  coverFileList.value = lesson.cover ? [
    {
      id: 'cover',
      name: '封面',
      status: 'finished',
      url: lesson.cover
    }
  ] : []
  
  showLessonForm.value = true
}

const resetLessonForm = () => {
  lessonForm.id = null
  lessonForm.title = ''
  lessonForm.description = ''
  lessonForm.sort_order = 0
  lessonForm.video_file_id = ''
  lessonForm.video_url = ''
  lessonForm.cover = ''
  lessonForm.duration = ''
  lessonForm.resolution = ''
  
  selectedVideoFile.value = null
  selectedCoverFile.value = null
  videoProgress.value = 0
  coverProgress.value = 0
  uploadingVideo.value = false
  
  videoPreviewUrl.value = ''
  coverFileList.value = []
}

const handleDeleteLesson = (lesson) => {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除该课时吗？',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteLesson(lesson.id)
        message.success('删除成功')
        fetchChapters()
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

// --- 腾讯云上传逻辑 ---

const handleFileChange = async ({ file }) => {
  selectedVideoFile.value = file.file
  // 本地预览
  if (file.file) {
    videoPreviewUrl.value = URL.createObjectURL(file.file)
    // 获取视频元数据
    try {
      const metadata = await getVideoMetadata(file.file)
      lessonForm.duration = metadata.duration
      lessonForm.resolution = metadata.resolution
    } catch (e) {
      console.error('获取视频元数据失败', e)
    }
  } else {
    videoPreviewUrl.value = ''
  }
}

const getVideoMetadata = (file) => {
  return new Promise((resolve) => {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.onloadedmetadata = () => {
      window.URL.revokeObjectURL(video.src);
      const duration = formatDuration(video.duration);
      const resolution = `${video.videoWidth}x${video.videoHeight}`;
      resolve({ duration, resolution });
    }
    video.onerror = () => {
      resolve({ duration: '', resolution: '' });
    }
    video.src = URL.createObjectURL(file);
  });
}

const formatDuration = (seconds) => {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

const handleCoverChange = ({ file, fileList }) => {
  // 暂存封面文件
  const url = URL.createObjectURL(file.file)
  selectedCoverFile.value = file.file
  coverPreviewUrl.value = url
  lessonForm.cover = url // 预览用
  
  // 更新 fileList 以便回显
  coverFileList.value = [{
    id: file.id,
    name: file.name,
    status: 'finished',
    url: url,
    file: file.file
  }]
}

const handleRemoveVideo = () => {
  selectedVideoFile.value = null
  videoPreviewUrl.value = ''
  lessonForm.video_file_id = ''
  lessonForm.video_url = ''
  lessonForm.duration = ''
  lessonForm.resolution = ''
}

const handleRemoveCover = () => {
  selectedCoverFile.value = null
  coverPreviewUrl.value = ''
  lessonForm.cover = ''
  coverFileList.value = []
}

const getSignature = async () => {
  const res = await getVodSignature()
  return res.signature
}

const processUpload = async () => {
  // 如果没有选择新文件，且已有 video_file_id，则不需要上传
  if (!selectedVideoFile.value && !selectedCoverFile.value) {
    return null
  }

  uploadingVideo.value = true
  videoProgress.value = 0
  coverProgress.value = 0

  try {
    // 如果选择了新视频，不传 fileId (生成新文件)
    // 如果只选择了封面，传 fileId (更新封面)
    const fileIdToPass = selectedVideoFile.value ? null : lessonForm.video_file_id

    const result = await uploadMediaFiles(
      selectedVideoFile.value,
      selectedCoverFile.value,
      getSignature,
      (info) => {
        videoProgress.value = Math.floor(info.percent * 100)
      },
      (info) => {
        coverProgress.value = Math.floor(info.percent * 100)
      },
      fileIdToPass // 传递 fileId 用于只更新封面的情况
    )
    
    const info = extractUploadInfo(result)
    return info
  } catch (error) {
    message.error('上传失败: ' + error.message)
    throw error
  } finally {
    uploadingVideo.value = false
  }
}

const submitLesson = async () => {
  if (!lessonForm.title) {
    message.warning('请输入课时标题')
    return
  }
  
  lessonSubmitting.value = true
  
  try {
    // 1. 先处理视频/封面上传
    if (selectedVideoFile.value || selectedCoverFile.value) {
      const uploadResult = await processUpload()
      if (uploadResult) {
        // 更新表单数据
        if (uploadResult.fileId) lessonForm.video_file_id = uploadResult.fileId
        if (uploadResult.mediaUrl) lessonForm.video_url = uploadResult.mediaUrl
        if (uploadResult.coverUrl) lessonForm.cover = uploadResult.coverUrl
      }
    }

    // 2. 提交到后端
    const data = {
      course: props.courseId,
      chapter: currentChapter.value.id,
      title: lessonForm.title,
      description: lessonForm.description,
      sort_order: lessonForm.sort_order,
      video_file_id: lessonForm.video_file_id,
      video_url: lessonForm.video_url,
      cover: lessonForm.cover,
      duration: lessonForm.duration,
      resolution: lessonForm.resolution
    }
    
    if (lessonForm.id) {
      await updateLesson(lessonForm.id, data)
      message.success('更新成功')
    } else {
      await createLesson(data)
      message.success('创建成功')
    }
    showLessonForm.value = false
    fetchChapters()
  } catch (error) {
    console.error(error)
    message.error(lessonForm.id ? '更新失败' : '创建失败')
  } finally {
    lessonSubmitting.value = false
  }
}

</script>

<style scoped>
.auth-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.chapter-modal, .chapter-form-modal, .lesson-form-modal {
  width: 1000px;
  max-width: 95vw;
}

.chapter-form-modal, .lesson-form-modal {
  width: 700px;
}

.auth-header {
  text-align: left;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.chapter-manager-content {
  min-height: 500px;
  max-height: 75vh;
  overflow-y: auto;
}

.chapter-footer {
  margin-top: 24px;
  text-align: center;
  border-top: 1px solid #f3f4f6;
  padding-top: 16px;
}

.chapter-list-container {
  /* margin-bottom: 20px; */
  border: 1px solid #efeff5;
  border-radius: 4px;
  padding: 16px;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-title {
  font-weight: 600;
  font-size: 15px;
  color: #555;
}

.chapter-desc {
  color: #9ca3af;
  font-size: 13px;
}

.lesson-list {
  padding: 0;
}

.n-list-item {
  padding: 0 !important;
}

.lesson-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 8px;
  transition: background-color 0.2s ease;
}

.lesson-item:hover {
  background: #f0f0f0;
}

.lesson-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lesson-title {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.lesson-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 12px;
  color: #999;
}

.lesson-actions {
  display: flex;
  gap: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.upload-progress {
  margin-top: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.progress-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.upload-text {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
  text-align: center;
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

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Adapt for both landscape and portrait */
}

/* Override Naive UI Upload Styles to match */
:deep(.n-upload-trigger.n-upload-trigger--image-card),
:deep(.n-upload-file-list .n-upload-file.n-upload-file--image-card-type) {
  width: 160px !important;
  height: 120px !important;
}

:deep(.n-upload-trigger.n-upload-trigger--image-card .n-upload-dragger) {
  padding: 0;
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
  margin-top: 8px;
  color: #666;
  font-size: 12px;
}

.progress-wrapper {
  margin-top: 8px;
  max-width: 300px;
}


</style>
