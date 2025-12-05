<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { NGrid, NGridItem, NCard, NTag, NIcon, NSpin, NEmpty, NSpace, NImage } from 'naive-ui'
import { PlayCircleOutline, CheckmarkCircle, DesktopOutline, TrendingUpOutline } from '@vicons/ionicons5'
import { getClientCourseList } from '@/api/courses'
import { getPlans } from '@/api/membership'

const router = useRouter()
const courses = ref([])
const loading = ref(false)

const fetchCourses = async () => {
  loading.value = true
  try {
    const res = await getClientCourseList()
    // Handle both standard pagination format and direct array
    courses.value = res.results || res.data || res || []
  } catch (error) {
    console.error('Failed to fetch courses:', error)
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push({ name: 'client-course-detail', params: { id } })
}

const getAccessLabel = (course) => {
  return course.access_level_name || `VIP Lv.${course.access_level}`
}

onMounted(() => {
  fetchCourses()
})
</script>

<template>
  <div class="course-list-page">
    <!-- Banner Section -->
    <div class="banner-wrapper">
      <section class="banner-section">
        <div class="banner-content">
          <div class="banner-text">
            <h1>视频课程</h1>
            <h2 class="subtitle">小白基础课程 + 实战项目</h2>
            <p class="description">
              课程体验设计合理，针对0基础的人非常友好，由浅入深，理论+实战的方式，帮你快速掌握COZE工作流、智能体搭建。配套实战项目，快速掌握AI应用技能。
            </p>
            <div class="tags-group">
              <div class="tag-item" style="--delay: 0.1s">
                <div class="banner-tag">
                  <span class="tag-icon">🌱</span> 零基础友好
                </div>
              </div>
              <div class="tag-item" style="--delay: 0.2s">
                <div class="banner-tag">
                  <span class="tag-icon">🎯</span> 理论+实战
                </div>
              </div>
              <div class="tag-item" style="--delay: 0.3s">
                <div class="banner-tag">
                  <span class="tag-icon">🔥</span> 持续更新
                </div>
              </div>
            </div>
          </div>
          <div class="banner-image">
            <div class="monitor-graphic">
              <div class="monitor-screen">
                <div class="play-button-graphic">
                  <div class="triangle"></div>
                </div>
              </div>
              <div class="monitor-stand"></div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Course List Section -->
    <section class="list-section">
      <div class="section-header">
        <h3>全部课程</h3>
      </div>
      
      <n-spin :show="loading">
        <div v-if="courses.length > 0">
            <n-grid :x-gap="24" :y-gap="24" cols="1 s:2 m:3 l:3" responsive="screen">
            <n-grid-item v-for="course in courses" :key="course.id">
                <n-card class="course-card" hoverable @click="goToDetail(course.id)" content-style="padding: 0;">
                <template #cover>
                    <div class="card-cover">
                    <img :src="course.cover || course.image" v-if="course.cover || course.image" alt="cover" class="cover-img" />
                    <div class="no-cover" v-else>
                        <div class="default-icon-wrapper">
                            <n-icon size="48" color="#ff7d18"><DesktopOutline /></n-icon>
                        </div>
                    </div>
                    <div class="cover-overlay">
                        <div class="play-btn">
                            <n-icon size="48"><PlayCircleOutline /></n-icon>
                            <span>开始学习</span>
                        </div>
                    </div>
                    <div class="access-badge free" v-if="course.access_level === 0">
                        免费
                    </div>
                    <div class="access-badge vip" v-else-if="course.access_level > 0">
                        {{ getAccessLabel(course) }}
                    </div>
                    </div>
                </template>
                <div class="card-content">
                    <h4 class="course-title">{{ course.title }}</h4>
                    <p class="course-subtitle">{{ course.description || '暂无简介' }}</p>
                    <div class="card-footer">
                        <div class="footer-left">
                             <span class="lesson-count">
                                {{ course.lesson_count || 0 }} 课时
                             </span>
                        </div>
                        <div class="footer-right">
                             <div class="status-badge" v-if="course.status === 'FINISHED'">
                                <n-icon size="12"><CheckmarkCircle /></n-icon> 已完结
                             </div>
                             <div class="status-badge updating" v-else>
                                <n-icon size="14"><TrendingUpOutline /></n-icon> 更新中
                             </div>
                        </div>
                    </div>
                </div>
                </n-card>
            </n-grid-item>
            </n-grid>
        </div>
        <n-empty v-else description="暂无课程" class="empty-state" />
      </n-spin>
    </section>
  </div>
</template>

<style scoped>
.course-list-page {
  min-height: 100vh;
  padding-bottom: 60px;
  padding-top: 20px;
}

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

/* Banner Styles */
.banner-section {
  background: linear-gradient(135deg, #fdf2e9 0%, #fcdfcc 100%);
  padding: 32px 40px;
  border-radius: 20px;
  box-shadow: 0 4px 20px #ff6b3526;
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.banner-text {
  flex: 1.6;
  max-width: none;
  padding-right: 20px;
}

.banner-text h1 {
  font-size: 42px;
  font-weight: 800;
  color: #263238;
  margin-top: 0;
  margin-bottom: 12px;
  line-height: 1.2;
  letter-spacing: -0.5px;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out forwards;
}

.subtitle {
  font-size: 24px;
  font-weight: 700;
  color: #ff6b35;
  margin-bottom: 0;
  display: inline-block;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.2s forwards;
}

.description {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
  max-width: 640px;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.4s forwards;
}

.tags-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.tag-item {
  opacity: 0;
  animation: slideUpFade 0.6s ease-out forwards;
  animation-delay: calc(0.5s + var(--delay, 0s));
}

@keyframes slideUpFade {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.banner-tag {
  padding: 8px 24px;
  border-radius: 50px;
  font-weight: 600;
  font-size: 15px;
  background: #ff6b35;
  color: #fff;
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  border: none;
}

.banner-tag:hover {
  transform: translateY(-3px);
  background: #ff5722;
  box-shadow: 0 12px 28px rgba(255, 107, 53, 0.4);
}

.tag-icon {
  font-size: 18px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

/* Dynamic Icon (Monitor Graphic) */
@media (max-width: 768px) {
  .banner-image {
    display: none;
  }
  
  .banner-text {
    padding-right: 0;
    text-align: center;
  }
  
  .tags-group {
    justify-content: center;
  }
  
  .banner-content {
    flex-direction: column;
  }
}

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

.play-button-graphic {
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

.play-button-graphic::before {
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

.play-button-graphic::after {
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

.monitor-screen:hover .play-button-graphic {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4);
}

.monitor-screen:hover .play-button-graphic::before,
.monitor-screen:hover .play-button-graphic::after {
  opacity: 1;
}

.triangle {
  width: 0;
  height: 0;
  border-left: 20px solid #fff;
  border-top: 12px solid transparent;
  border-bottom: 12px solid transparent;
  margin-left: 6px; /* Optical adjustment */
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

/* List Section */
.list-section {
  max-width: 1200px;
  margin: 40px auto 0;
  padding: 40px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 20px 60px #0000001a;
}

@media (max-width: 1240px) {
  .list-section {
    margin-left: 20px;
    margin-right: 20px;
  }
}

.section-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 16px;
  border-left: none;
  padding-left: 0;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 400;
  color: #333;
  margin: 0;
}

/* Course Card Styles */
.course-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #f0f0f0;
  height: 100%;
  cursor: pointer;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
}

.course-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

.card-cover {
  height: 180px;
  background: #fff9f2;
  position: relative;
  overflow: hidden;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.course-card:hover .cover-img {
  transform: scale(1.1); /* 放大效果 */
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.course-card:hover .cover-overlay {
  opacity: 1;
}

.play-btn {
  background: transparent;
  color: #fff;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  transform: translateY(20px);
  transition: transform 0.3s ease;
  box-shadow: none;
}

.course-card:hover .play-btn {
  transform: translateY(0);
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-icon-wrapper {
  width: 80px;
  height: 80px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 125, 24, 0.15);
}

.access-badge {
  position: absolute;
  top: 0;
  left: 0;
  padding: 6px 16px;
  border-radius: 16px 0 16px 0;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  z-index: 2;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.access-badge.free {
  background: linear-gradient(135deg, #18a058 0%, #2080f0 100%);
}

.access-badge.vip {
  background: linear-gradient(135deg, #ff7d18 0%, #ff4d4f 100%);
  overflow: hidden;
}

/* Shine Effect */
.access-badge.vip::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-25deg);
  animation: shine 5s infinite;
}

@keyframes shine {
  0% { left: -100%; }
  50% { left: 200%; }
  100% { left: 200%; }
}

.card-content {
  padding: 14px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.course-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px;
  line-height: 2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-subtitle {
  font-size: 15px;
  color: #8c8c8c;
  margin: 0 0 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 8px;
  border-top: none;
}

.lesson-count {
  font-size: 14px;
  color: #999;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 12px;
  font-weight: 600;
  background-color: rgba(24, 160, 88, 0.1);
  color: #18a058;
  border: 1px solid rgba(24, 160, 88, 0.2);
}

.status-badge.updating {
  background-color: rgba(32, 128, 240, 0.1);
  color: #2080f0;
  border: 1px solid rgba(32, 128, 240, 0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .banner-content {
    flex-direction: column-reverse;
    text-align: center;
    padding: 16px;
  }
  
  .banner-text h1 {
    font-size: 28px;
  }
  
  .tags-group {
    justify-content: center;
    flex-wrap: wrap;
  }

  .list-section {
    padding: 20px;
    margin-top: 20px;
  }
}
</style>
