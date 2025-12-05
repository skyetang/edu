<template>
  <div class="workflow-page">
    <!-- Banner Section -->
    <div class="banner-wrapper">
      <div class="banner-section">
        <div class="banner-content">
          <div class="banner-text">
            <h1 class="banner-title">工作流案例</h1>
            <p class="banner-subtitle">丰富的工作流案例，覆盖多个AI应用领域</p>
            <p class="banner-desc">
              汇聚最新最热门的AI工作流模板，涵盖办公自动化、内容创作、数据分析等多个领域。每个工作流都经过精心测试和优化，持续更新，紧跟AI技术发展趋势。
            </p>
            <div class="banner-tags">
              <div class="tag-item" style="--delay: 0.1s">
                <n-icon size="18" color="#fff"><CodeSlashOutline /></n-icon>
                <span>提供源码</span>
              </div>
              <div class="tag-item" style="--delay: 0.2s">
                <n-icon size="18" color="#fff"><FlashOutline /></n-icon>
                <span>高效自动化</span>
              </div>
              <div class="tag-item" style="--delay: 0.3s">
                <n-icon size="18" color="#fff"><TimeOutline /></n-icon>
                <span>持续更新</span>
              </div>
            </div>
          </div>
          <div class="banner-image">
            <div class="ai-circle">
              <div class="ai-inner">AI</div>
              <div class="ripple r1"></div>
              <div class="ripple r2"></div>
              <div class="ripple r3"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <div class="sidebar-header">
          <n-icon size="22" color="#333"><AppsOutline /></n-icon>
          <span class="sidebar-title">分类导航</span>
        </div>
        <div class="category-list">
          <div 
            class="category-item" 
            :class="{ active: !currentCategory }"
            @click="handleCategoryChange(null)"
          >
            <span class="cat-name">全部工作流</span>
            <n-icon class="arrow-icon"><ChevronForwardOutline /></n-icon>
          </div>
          <div 
            v-for="cat in categories" 
            :key="cat.id"
            class="category-item"
            :class="{ active: currentCategory === cat.id }"
            @click="handleCategoryChange(cat.id)"
          >
            <span class="cat-name">{{ cat.name }}</span>
            <n-icon class="arrow-icon"><ChevronForwardOutline /></n-icon>
          </div>
        </div>
      </div>

      <!-- Right Content -->
      <div class="content-area">
        <!-- Filter Bar -->
        <div class="filter-bar">
          <div class="filter-left">
            <div class="section-title">{{ currentCategoryName }}</div>
            <span class="result-count" v-if="!loading">共 {{ total }} 个结果</span>
          </div>
          <div class="filter-actions">
            <n-input 
              v-model:value="searchQuery" 
              placeholder="搜索工作流..." 
              round
              clearable
              @keyup.enter="handleSearch"
              class="search-input"
            >
              <template #prefix>
                <n-icon :component="SearchOutline" />
              </template>
            </n-input>
            <n-select 
              v-model:value="sortBy" 
              :options="sortOptions" 
              style="width: 140px" 
              size="medium"
              @update:value="handleSortChange"
            />
          </div>
        </div>

        <!-- Workflow List -->
        <n-spin :show="loading">
          <div v-if="workflows.length > 0" class="workflow-grid">
            <div 
              v-for="wf in workflows" 
              :key="wf.id" 
              class="workflow-card"
              @click="goDetail(wf)"
            >
              <div class="card-cover">
                <img :src="wf.cover || defaultCover" alt="cover" />
                <div class="permission-tag" :class="getPermissionClass(wf.access_level)">
                  {{ wf.access_level_name || (wf.access_level === 0 ? '免费' : 'VIP') }}
                </div>
                <div class="hover-overlay">
                  <div class="view-btn">查看详情</div>
                </div>
              </div>
              <div class="card-info">
                <h3 class="card-title">{{ wf.title }}</h3>
                <p class="card-desc">{{ wf.description || '暂无描述' }}</p>
                <div class="card-footer">
                  <div class="card-author">
                    <n-avatar round size="small" src="/logo.png" fallback-src="https://07akioni.oss-cn-beijing.aliyuncs.com/07akioni.jpeg" />
                    <span class="author-name">贝塔AI</span>
                  </div>
                  <span class="date">{{ formatDate(wf.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <n-empty description="暂无相关工作流" />
          </div>
          
          <!-- Pagination -->
          <div class="pagination-container" v-if="total > pageSize">
            <n-pagination
              v-model:page="page"
              :page-size="pageSize"
              :item-count="total"
              @update:page="handlePageChange"
            />
          </div>
        </n-spin>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  NIcon, NInput, NSelect, NSpin, NEmpty, NPagination, NAvatar
} from 'naive-ui'
import { 
  CodeSlashOutline, 
  FlashOutline, 
  TimeOutline,
  SearchOutline,
  AppsOutline,
  ChevronForwardOutline
} from '@vicons/ionicons5'
import { getWorkflowCategories, getWorkflows } from '@/api/workflows'

const router = useRouter()

// State
const loading = ref(false)
const categories = ref([])
const workflows = ref([])
const currentCategory = ref(null)
const searchQuery = ref('')
const sortBy = ref('newest')
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const defaultCover = 'https://via.placeholder.com/300x200?text=Workflow'

// Options
const sortOptions = [
  { label: '最新发布', value: 'newest' },
  { label: '最早发布', value: 'oldest' },
  { label: '排序值', value: 'sort' }
]

// Computed
const currentCategoryName = computed(() => {
  if (!currentCategory.value) return '全部工作流'
  const cat = categories.value.find(c => c.id === currentCategory.value)
  return cat ? cat.name : '全部工作流'
})

// Methods
const fetchCategories = async () => {
  try {
    const res = await getWorkflowCategories()
    categories.value = res.data || res
  } catch (error) {
    console.error('Failed to fetch categories', error)
  }
}

const fetchWorkflowsData = async () => {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      category: currentCategory.value,
      status: 'PUBLISHED'
    }
    
    if (sortBy.value === 'newest') params.ordering = '-created_at'
    if (sortBy.value === 'oldest') params.ordering = 'created_at'
    if (sortBy.value === 'sort') params.ordering = 'sort_order'

    const res = await getWorkflows(params)
    workflows.value = res.data || res.results || []
    if (res.meta?.pagination) {
      total.value = res.meta.pagination.total
    } else {
      total.value = res.count || 0
    }
  } catch (error) {
    console.error('Failed to fetch workflows', error)
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = (id) => {
  currentCategory.value = id
  page.value = 1
  fetchWorkflowsData()
}

const handleSearch = () => {
  page.value = 1
  fetchWorkflowsData()
}

const handleSortChange = () => {
  page.value = 1
  fetchWorkflowsData()
}

const handlePageChange = (p) => {
  page.value = p
  fetchWorkflowsData()
}

const goDetail = (wf) => {
  // TODO: Implement detail page navigation
  console.log('Go to detail', wf.id)
}

const getPermissionClass = (level) => {
  if (level === 0) return 'tag-free'
  return 'tag-vip'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  fetchCategories()
  fetchWorkflowsData()
})
</script>

<style scoped>
.workflow-page {
  min-height: 100vh;
  background-color: #f8f9fa; /* Slightly lighter background */
  padding-top: 20px;
  padding-bottom: 60px;
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

/* Banner */
.banner-section {
  background: linear-gradient(135deg, #fdf2e9 0%, #fcdfcc 100%); /* Match CourseList */
  padding: 32px 40px; /* Match CourseList */
  margin-bottom: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(255, 107, 53, 0.15);
}

.banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
}

.banner-text {
  flex: 1;
  max-width: 650px;
}

.banner-title {
  font-size: 42px;
  font-weight: 800;
  color: #263238;
  margin-bottom: 12px;
  line-height: 1.2;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out forwards;
}

.banner-subtitle {
  font-size: 24px;
  font-weight: 700;
  color: #ff6b35;
  margin-bottom: 16px;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.2s forwards;
}

.banner-desc {
  font-size: 16px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 32px;
  opacity: 0;
  animation: slideUpFade 0.8s ease-out 0.4s forwards;
}

.banner-tags {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #ff6b35;
  color: #fff;
  padding: 8px 20px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3);
  transition: transform 0.2s;
  opacity: 0;
  animation: slideUpFade 0.6s ease-out forwards;
  animation-delay: calc(0.5s + var(--delay, 0s));
}

.tag-item:hover {
  transform: translateY(-3px);
}

/* Animations */
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

/* AI Circle Animation (Simplified Monitor Graphic Replacement) */
.banner-image {
  flex: 0.8;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ai-circle {
  width: 180px;
  height: 180px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.ai-inner {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #ff8f00, #ff4400);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 32px;
  font-weight: bold;
  z-index: 10;
  box-shadow: 0 8px 24px rgba(255, 102, 0, 0.4);
}

.ripple {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 102, 0, 0.3);
  animation: ripple 3s infinite linear;
}

.r1 { width: 120px; height: 120px; animation-delay: 0s; }
.r2 { width: 160px; height: 160px; animation-delay: 1s; }
.r3 { width: 200px; height: 200px; animation-delay: 2s; }

@keyframes ripple {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

/* Main Container */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

@media (max-width: 1240px) {
  .main-container {
    padding: 0 20px;
  }
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  flex-shrink: 0;
  position: sticky;
  top: 80px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
  padding-left: 12px;
}

.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: #555;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.category-item:hover {
  background-color: #fff9f5;
  color: #ff6b35;
}

.category-item.active {
  background-color: #fff5eb;
  color: #ff6b35;
  font-weight: 600;
}

.category-item.active .arrow-icon {
  opacity: 1;
  transform: translateX(0);
  color: #ff6b35;
}

.arrow-icon {
  font-size: 16px;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.2s;
  color: #999;
}

.category-item:hover .arrow-icon {
  opacity: 0.5;
  transform: translateX(0);
}

/* Content Area */
.content-area {
  flex: 1;
}

.filter-bar {
  background: #fff;
  padding: 20px 24px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.filter-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.result-count {
  font-size: 14px;
  color: #999;
}

.filter-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  width: 240px;
}

/* Grid */
.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.workflow-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  border: 1px solid #f5f5f5;
  display: flex;
  flex-direction: column;
}

.workflow-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.08);
}

.card-cover {
  height: 160px;
  background-color: #f9f9f9;
  position: relative;
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.workflow-card:hover .card-cover img {
  transform: scale(1.05);
}

.permission-tag {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  z-index: 2;
}

.tag-free {
  background-color: rgba(24, 160, 88, 0.9);
}

.tag-vip {
  background-color: rgba(255, 107, 53, 0.9);
}

.hover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.workflow-card:hover .hover-overlay {
  opacity: 1;
}

.view-btn {
  color: #fff;
  border: 1px solid #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(4px);
}

.card-info {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin: 0 0 8px;
  line-height: 1.4;
}

.card-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 16px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.card-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-name {
  font-size: 12px;
  color: #888;
}

.date {
  font-size: 12px;
  color: #999;
}

.empty-state {
  padding: 80px;
  display: flex;
  justify-content: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 50px;
}

@media (max-width: 768px) {
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .banner-text {
    padding-right: 0;
  }
  
  .banner-tags {
    justify-content: center;
  }
  
  .main-container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    position: static;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filter-actions {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
}
</style>