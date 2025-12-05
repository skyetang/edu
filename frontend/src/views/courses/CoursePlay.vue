<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin, NButton, NResult, NIcon, NEmpty, NTag } from 'naive-ui'
import { ChevronBackOutline, ListOutline, PlayCircleOutline, LockClosedOutline } from '@vicons/ionicons5'
import { getClientCourseDetail } from '@/api/courses'
import { getVodPlaySignature } from '@/api/common'
import VideoPlayer from '@/components/VideoPlayer.vue'

const route = useRoute()
const router = useRouter()

const courseId = route.params.id
const lessonId = ref(route.params.lessonId)

const course = ref(null)
const authLoading = ref(false)
const playerError = ref(null)
const playAuth = ref(null)

// Computed properties for lessons
const allLessons = computed(() => {
  if (!course.value || !course.value.chapters) return []
  const lessons = []
  course.value.chapters.forEach(chapter => {
    if (chapter.lessons) {
      lessons.push(...chapter.lessons)
    }
  })
  return lessons
})

const currentLesson = computed(() => {
  return allLessons.value.find(l => l.id == lessonId.value)
})

const prevLesson = computed(() => {
  const index = allLessons.value.findIndex(l => l.id == lessonId.value)
  if (index > 0) return allLessons.value[index - 1]
  return null
})

const nextLesson = computed(() => {
  const index = allLessons.value.findIndex(l => l.id == lessonId.value)
  if (index !== -1 && index < allLessons.value.length - 1) {
    return allLessons.value[index + 1]
  }
  return null
})

// Fetch Course Structure
const fetchCourse = async () => {
  try {
    const res = await getClientCourseDetail(courseId)
    course.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch course:', error)
  }
}

// Fetch Play Auth
const fetchPlayAuth = async () => {
  if (!lessonId.value) return
  
  // Ensure course is loaded
  if (!course.value) {
    await fetchCourse()
  }
  
  if (!currentLesson.value || !currentLesson.value.video_file_id) {
    playerError.value = {
      type: 'error',
      message: '找不到课时视频信息'
    }
    return
  }

  authLoading.value = true
  playerError.value = null
  
  try {
    const res = await getVodPlaySignature(currentLesson.value.video_file_id)
    playAuth.value = res
  } catch (error) {
    console.error('Play auth failed:', error)
    if (error.code === 'AUTH_EXPIRED' || error.code === 'PERMISSION_DENIED') {
      playerError.value = {
        type: 'permission',
        message: error.message || '无权观看此视频，请升级会员'
      }
    } else {
      playerError.value = {
        type: 'error',
        message: '视频加载失败，请稍后重试'
      }
    }
  } finally {
    authLoading.value = false
  }
}

const switchLesson = (id) => {
  if (id == lessonId.value) return
  lessonId.value = id
  router.replace({ params: { ...route.params, lessonId: id } })
  // fetchPlayAuth will be triggered by watch or we call it directly
  // Since we watch lessonId below, it might be better to let watcher handle it
  // But for explicit switch, we can ensure it updates.
}

const goBack = () => {
  router.push({ name: 'client-course-detail', params: { id: courseId } })
}

onMounted(async () => {
  await fetchCourse()
  fetchPlayAuth()
})

// Watch for route param changes
watch(() => route.params.lessonId, (newId) => {
  if (newId && newId !== lessonId.value) {
    lessonId.value = newId
    fetchPlayAuth()
  }
})
</script>

<template>
  <div class="course-play-page">
    <!-- Top Bar -->
    <header class="play-header">
      <div class="header-container">
        <div class="header-left">
          <n-button text @click="goBack" class="back-btn">
            <template #icon><n-icon><ChevronBackOutline /></n-icon></template>
            返回课程详情
          </n-button>
          <span class="divider">|</span>
          <h2 class="course-name" v-if="course">{{ course.title }}</h2>
        </div>
      </div>
    </header>

    <div class="play-wrapper">
      <div class="play-container">
        <!-- Left: Video Player -->
        <div class="video-section">
        <div class="player-wrapper">
          <n-spin :show="authLoading" description="正在获取播放权限..." style="width: 100%; height: 100%">
            <div style="width: 100%; height: 100%">
              <!-- Video Player Component -->
              <VideoPlayer
                v-if="playAuth && !playerError && currentLesson"
                :file-id="currentLesson.video_file_id"
                :signature="playAuth.signature"
                :app-id="playAuth.app_id"
                :license-url="playAuth.license_url"
                :prev-lesson="prevLesson"
                :current-lesson="currentLesson"
                :next-lesson="nextLesson"
                @switch="switchLesson"
              />
            </div>
            
            <!-- Error/Permission Overlay -->
            <div class="player-overlay" v-if="playerError">
              <n-result
                status="403"
                :title="playerError.type === 'permission' ? '需要会员权限' : '播放出错'"
                :description="playerError.message"
              >
                <template #footer>
                  <n-button type="primary" @click="router.push('/membership')" v-if="playerError.type === 'permission'">
                    立即升级会员
                  </n-button>
                  <n-button @click="fetchPlayAuth" v-else>
                    重试
                  </n-button>
                </template>
              </n-result>
            </div>
          </n-spin>

        </div>
        
        <!-- Current Lesson Info -->
        <div class="lesson-meta" v-if="!playerError && !authLoading">
          <h3>正在播放</h3>
        </div>
      </div>

      <!-- Right: Directory -->
      <div class="directory-section">
        <div class="dir-header">
          <n-icon><ListOutline /></n-icon>
          <span>课程目录</span>
        </div>
        
        <div class="dir-content" v-if="course">
          <div v-for="(chapter, index) in course.chapters" :key="chapter.id" class="chapter-group">
            <div class="chapter-title">第{{ index + 1 }}章 {{ chapter.title }}</div>
            <div 
              v-for="(lesson, lIndex) in chapter.lessons" 
              :key="lesson.id"
              class="lesson-row"
              :class="{ active: lesson.id == lessonId }"
              @click="switchLesson(lesson.id)"
            >
              <div class="row-left">
                <n-icon class="status-icon" v-if="lesson.id == lessonId"><PlayCircleOutline /></n-icon>
                <span class="row-num">{{ index + 1 }}-{{ lIndex + 1 }}</span>
                <span class="row-title">{{ lesson.title }}</span>
              </div>
              <div class="row-right">
                <n-tag size="tiny" :bordered="false" v-if="course.access_level > 0">{{ course.access_level_name || `VIP Lv.${course.access_level}` }}</n-tag>
                <n-tag size="tiny" type="success" :bordered="false" v-else>免费</n-tag>
              </div>
            </div>
          </div>
        </div>
        <n-empty v-else description="加载中..." class="mt-8" />
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
.course-play-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #1a1a1a;
  color: #fff;
}

.play-header {
  height: 60px;
  background-color: #222;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0,0,0,0.2);
  z-index: 10;
}

.header-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
  display: flex;
  align-items: center;
}

@media (max-width: 1640px) {
  .header-container {
    padding: 0 20px;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.play-wrapper {
  flex: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  overflow: hidden;
  background-color: #1a1a1a;
}

.play-container {
  width: 100%;
  max-width: 1600px;
  height: 100%;
  display: flex;
  background-color: #000;
  box-shadow: 0 0 30px rgba(0,0,0,0.5);
}

.back-btn {
  color: #ccc;
}

.back-btn:hover {
  color: #fff;
}

.divider {
  color: #444;
}

.course-name {
  font-size: 16px;
  margin: 0;
  font-weight: 500;
}

/* Video Section */
.video-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #000;
  position: relative;
}

.player-wrapper {
  width: 100%;
  height: 100%; /* Fill available space */
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

:deep(.n-spin-content) {
  width: 100%;
  height: 100%;
}

.video-player {
  width: 100%;
  height: 100%;
}

.player-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.85);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 20;
}

/* Directory Section */
.directory-section {
  width: 320px;
  background-color: #222;
  border-left: 1px solid #333;
  display: flex;
  flex-direction: column;
}

.dir-header {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid #333;
  font-size: 16px;
  font-weight: 500;
}

.dir-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.chapter-group {
  margin-bottom: 16px;
}

.chapter-title {
  padding: 8px 16px;
  font-size: 14px;
  color: #999;
  font-weight: 600;
}

.lesson-row {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.lesson-row:hover {
  background-color: #333;
}

.lesson-row.active {
  background-color: #2a4c38; /* Green tint */
  color: #18a058;
}

.row-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow: hidden;
}

.row-title {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-num {
  font-size: 12px;
  color: #666;
  min-width: 32px;
}

.lesson-row.active .row-num {
  color: #18a058;
}

/* Scrollbar */
.dir-content::-webkit-scrollbar {
  width: 6px;
}
.dir-content::-webkit-scrollbar-track {
  background: #222;
}
.dir-content::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 3px;
}

@media (max-width: 768px) {
  .play-container {
    flex-direction: column;
  }
  .directory-section {
    width: 100%;
    height: 40%; /* Take bottom part on mobile */
  }
  .video-section {
    height: 60%;
  }
}
</style>