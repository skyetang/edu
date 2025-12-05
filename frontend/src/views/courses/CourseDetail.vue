<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSpin, NTag, NIcon, NCollapse, NCollapseItem, NList, NListItem, NButton, NEmpty, NAvatar, useDialog, useMessage } from 'naive-ui'
import { 
  PlayCircleOutline, 
  TimeOutline, 
  PersonOutline,
  BookOutline,
  LockClosedOutline,
  VideocamOutline,
  ChevronBack
} from '@vicons/ionicons5'
import { getClientCourseDetail } from '@/api/courses'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const dialog = useDialog()
const message = useMessage()
const courseId = route.params.id
const course = ref(null)
const loading = ref(false)
const fetchCourseDetail = async () => {
  loading.value = true
  try {
    const res = await getClientCourseDetail(courseId)
    course.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch course detail:', error)
  } finally {
    loading.value = false
  }
}

const checkPermission = () => {
  if (!authStore.isLoggedIn) {
    message.warning('请先登录')
    authStore.openLoginModal()
    return false
  }

  if (course.value.access_level > 0) {
    const user = authStore.user
    const isExpired = user.membership_expire_at && new Date(user.membership_expire_at) < new Date()
    
    if (user.level < course.value.access_level || isExpired) {
       const requiredLevel = course.value.access_level_name || `VIP Lv.${course.value.access_level}`
       
       dialog.warning({
        title: '权限不足',
        content: `此课程需要开通 ${requiredLevel} 才能观看`,
        positiveText: '去开通',
        negativeText: '取消',
        onPositiveClick: () => {
          router.push('/membership')
        }
      })
      return false
    }
  }
  return true
}

const startLearning = () => {
  if (!checkPermission()) return

  // Find first lesson
  if (course.value?.chapters?.length > 0) {
    const firstChapter = course.value.chapters[0]
    if (firstChapter.lessons?.length > 0) {
      goToLesson(firstChapter.lessons[0].id, true) // Pass true to skip check since we just checked
      return
    }
  }
  // Fallback or show message
}

const goToLesson = (lessonId, skipCheck = false) => {
  if (!skipCheck && !checkPermission()) return

  router.push({ 
    name: 'client-course-play', 
    params: { id: courseId, lessonId } 
  })
}

onMounted(() => {
  fetchCourseDetail()
})
</script>

<template>
  <div class="course-detail-page">
    <n-spin :show="loading">
      <div v-if="course">
        <!-- Banner Section -->
        <div class="banner-wrapper">
          <section class="banner-section">
            <div class="banner-content">
              <div class="banner-text">
                <div class="badge-row">
                  <n-tag type="success" round size="small" v-if="course.status === 'FINISHED'">已完结</n-tag>
                  <n-tag type="warning" round size="small" v-else>更新中</n-tag>
                  <n-tag type="error" round size="small" v-if="course.is_membership" class="ml-2">VIP会员</n-tag>
                </div>
                
                <h1 class="course-title">{{ course.title }}</h1>
                
                <p class="description">
                  {{ course.description || '暂无课程简介' }}
                </p>

                <div class="course-meta">
                  <span class="meta-item">
                    <n-icon><PersonOutline /></n-icon>
                    讲师：{{ course.instructor }}
                  </span>
                  <span class="meta-item">
                    <n-icon><BookOutline /></n-icon>
                    分类：{{ course.category_name }}
                  </span>
                  <span class="meta-item">
                    <n-icon><TimeOutline /></n-icon>
                    更新时间：{{ new Date(course.updated_at).toLocaleDateString() }}
                  </span>
                </div>
                
                <div class="action-btn">
                  <n-button class="start-btn" type="primary" size="large" round @click="startLearning">
                    <template #icon><n-icon><PlayCircleOutline /></n-icon></template>
                    开始学习
                  </n-button>
                </div>
              </div>
              
              <div class="banner-image">
                <div class="monitor-graphic">
                  <div class="monitor-screen glass-effect">
                    <div class="play-icon-wrapper">
                      <n-icon size="48" color="#fff">
                        <PlayCircleOutline />
                      </n-icon>
                    </div>
                  </div>
                  <div class="monitor-stand"></div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Back Button Section -->
        <div class="nav-bar">
          <n-button class="back-btn" color="#ff6b35" @click="router.push('/courses')">
            <template #icon><n-icon color="#fff"><ChevronBack /></n-icon></template>
            返回课程列表
          </n-button>
        </div>

        <!-- Course Content Section -->
        <section class="content-section">
          <div class="section-header">
            <h3>课程目录</h3>
          </div>
          
          <div class="chapter-list" v-if="course.chapters && course.chapters.length > 0">
            <div 
              v-for="(chapter, index) in course.chapters" 
              :key="chapter.id" 
              class="chapter-card"
            >
              <div class="chapter-header">
                <div class="chapter-num">{{ index + 1 }}</div>
                <h4 class="chapter-title">{{ chapter.title }}</h4>
              </div>
              
              <div class="lesson-list" v-if="chapter.lessons && chapter.lessons.length > 0">
                <div 
                  v-for="(lesson, lIndex) in chapter.lessons" 
                  :key="lesson.id"
                  class="lesson-row"
                  @click="goToLesson(lesson.id)"
                >
                  <div class="lesson-left">
                    <n-icon class="video-icon"><VideocamOutline /></n-icon>
                    <span class="lesson-name">{{ lesson.title }}</span>
                  </div>
                  <div class="lesson-right">
                    <span class="lesson-duration" v-if="lesson.duration">{{ lesson.duration }}</span>
                    <span class="lesson-duration" v-else>10:00</span>
                    <span class="vip-tag" v-if="course.access_level > 0">{{ course.access_level_name || `VIP Lv.${course.access_level}` }}</span>
                    <span class="free-tag" v-else>免费</span>
                  </div>
                </div>
              </div>
              <div v-else class="no-lessons">
                暂无课时
              </div>
            </div>
          </div>
          <n-empty v-else description="暂无章节内容" class="mt-8" />
        </section>
      </div>
    </n-spin>
  </div>
</template>

<style scoped>
.course-detail-page {
  min-height: calc(100vh - 64px);
  padding-top: 20px;
}

/* Banner Styles (Consistent with CourseList) */
.banner-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 1240px) {
  .banner-wrapper {
    padding: 0 20px;
  }
}

.banner-section {
  background: linear-gradient(135deg, #fdf2e9 0%, #fcdfcc 100%);
  padding: 32px 40px;
  border-radius: 20px;
  box-shadow: 0 8px 24px #ff6b351f,0 4px 12px #ff6b3514;
  margin-bottom: 32px;
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
}

.banner-text {
  flex: 1.6;
  max-width: none;
  padding-right: 40px;
}

.course-title {
  font-size: 42px;
  font-weight: 800;
  color: #d97706;
  margin: 16px 0;
  line-height: 1.2;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out forwards;
}

.badge-row {
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.1s forwards;
}

.course-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  color: #666;
  font-size: 15px;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.3s forwards;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.description {
  font-size: 16px;
  color: #555;
  line-height: 1.7;
  margin-bottom: 22px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.2s forwards;
}

.action-btn {
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.4s forwards;
}

@keyframes slideUpFade {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

.ml-2 {
  margin-left: 8px;
}

@media (max-width: 768px) {
  .banner-content {
    flex-direction: column;
    gap: 24px;
  }
  
  .banner-text {
    padding-right: 0;
    text-align: center;
  }
  
  .banner-image {
    display: none;
  }
  
  .course-meta {
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .badge-row {
    justify-content: center;
    display: flex;
  }
  
  .description {
    margin-bottom: 20px;
  }
}

/* Monitor Graphic Styles */
.banner-image {
  flex: 0.8;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.monitor-graphic {
  width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.monitor-screen {
  width: 100%;
  height: 150px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.2));
  backdrop-filter: blur(12px);
  border-radius: 24px;
  box-shadow: 
    0 12px 40px 0 rgba(255, 107, 53, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.6);
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.play-icon-wrapper {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ff9c6e, #ff6b35);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(255, 107, 53, 0.3);
  transition: all 0.3s ease;
  position: relative;
  z-index: 2;
}

.play-icon-wrapper::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  opacity: 0;
  transition: opacity 0.3s;
}

.play-icon-wrapper::after {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.4);
  animation: pulse 2s infinite;
  opacity: 0;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.5); opacity: 0; }
}

.monitor-screen:hover .play-icon-wrapper {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4);
}

.monitor-screen:hover .play-icon-wrapper::before {
  opacity: 1;
}

.monitor-screen:hover .play-icon-wrapper::after {
  opacity: 1;
}

.vip-tag {
  background: linear-gradient(135deg, #ffd591 0%, #ffa940 100%);
  color: #fff;
  border: none;
  font-weight: 600;
  padding: 0 10px;
  height: 24px;
  line-height: 24px;
  border-radius: 12px;
  font-size: 12px;
}

.free-tag {
  background: linear-gradient(135deg, #85e0a3 0%, #52c41a 100%);
  color: #fff;
  border: none;
  font-weight: 600;
  padding: 0 10px;
  height: 24px;
  line-height: 24px;
  border-radius: 12px;
  font-size: 12px;
}

.lesson-duration {
  color: #999;
  font-size: 13px;
  margin-right: 12px;
  font-weight: 500;
}

.monitor-stand {
  width: 80px;
  height: 20px;
  background: linear-gradient(to bottom, rgba(255, 107, 53, 0.15), rgba(255, 107, 53, 0.05));
  backdrop-filter: blur(4px);
  margin-top: 16px;
  border-radius: 10px;
  z-index: -1;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.1);
}

/* Content Section */
.content-section {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 16px #00000014;
  margin-bottom: 40px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

@media (max-width: 1240px) {
  .content-section {
    margin-left: 20px;
    margin-right: 20px;
    width: auto;
  }
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 16px;
}

.section-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

/* Nav Bar */
.nav-bar {
  max-width: 1200px;
  margin: 0 auto 20px;
  padding: 0;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1240px) {
  .nav-bar {
    padding: 0 20px;
  }
}

.back-btn {
  font-weight: 500;
  color: #fff;
  border-radius: 8px;
  padding: 0 20px;
  height: 40px;
  background: linear-gradient(135deg, #ff9c6e 0%, #ff6b35 100%);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
  transition: all 0.3s ease;
  border: none;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 107, 53, 0.4);
}

.start-btn {
  background: rgba(255, 107, 53, 0.9);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
  transition: all 0.3s ease;
  padding: 0 32px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 9999px;
}

.start-btn:hover {
  background: #ff6b35;
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(255, 107, 53, 0.4);
}

/* Chapter List Styles */
.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.chapter-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
  overflow: hidden;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #fafafa;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 0;
}

.chapter-num {
  width: 32px;
  height: 32px;
  background: #ff6b35;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(255, 107, 53, 0.3);
}

.chapter-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.lesson-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 12px 16px; /* Add padding */
}

.lesson-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: transparent;
  /* border-bottom: 1px solid #f5f5f5; Remove border */
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 6px;
  border-radius: 8px; /* Rounded corners for hover effect */
}

.lesson-row:hover {
  background: #fff3e6; /* Deeper hover color */
}

.lesson-left {
  display: flex;
  align-items: center;
  gap: 12px; /* Increased gap */
}

.video-icon {
  color: #ff7d18; /* Theme color */
  font-size: 22px; /* Larger icon */
  opacity: 0.8;
}

.lesson-row:hover .video-icon {
  color: #ff6b35;
  opacity: 1;
}

.lesson-name {
  font-size: 16px; /* Larger font */
  color: #263238; /* Darker text */
  font-weight: 500; /* Slightly bolder */
}

.lesson-row:hover .lesson-name {
  color: #ff6b35;
}

.lesson-right {
  display: flex;
  align-items: center;
}

.lesson-duration {
  color: #666; /* Darker grey */
  font-size: 14px; /* Larger font */
  margin-right: 16px;
  font-weight: 500;
}

/* Updated Tags */
.vip-tag {
  background: linear-gradient(135deg, gold, #ff8f00);
  color: #8b4513;
  border: none;
  font-weight: 700;
  padding: 0 14px;
  height: 26px;
  line-height: 26px;
  border-radius: 12px;
  font-size: 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 2px 6px rgba(255, 143, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.4);
  display: inline-block;
}

.lesson-row:hover .vip-tag {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(255, 143, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.free-tag {
  background: #f6ffed; /* Light green bg */
  color: #52c41a; /* Green text */
  border: 1px solid #b7eb8f;
  font-weight: 600;
  padding: 0 12px;
  height: 26px;
  line-height: 24px;
  border-radius: 13px;
  font-size: 12px;
  transition: all 0.3s;
}

.lesson-row:hover .free-tag {
  background: #52c41a;
  color: #fff;
  border-color: #52c41a;
}

.no-lessons {
  padding: 32px;
  text-align: center;
  color: #999;
  font-size: 14px;
  background: transparent;
  margin-top: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .banner-content {
    flex-direction: column-reverse;
    text-align: center;
    padding: 0 20px;
  }
  
  .banner-text {
    margin-top: 20px;
  }
  
  .course-meta {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .monitor-graphic {
    width: 100%;
    max-width: 320px;
  }
  
  .content-section {
    padding: 20px;
  }
}
</style>
