<script setup>
import { RocketOutline, BookOutline, PeopleOutline, ChevronBack, ChevronForward, Play, GitNetworkOutline, CubeOutline, FlashOutline } from '@vicons/ionicons5'
import { NIcon, NCarousel, NCarouselItem } from 'naive-ui'
import { ref } from 'vue'

const carouselSlides = [
  {
    key: 'course',
    title: '专业',
    highlight: '课程',
    subtitle: '系统性学习AI智能体，从入门到精通',
    description: '高质量视频课程，配套实战项目，由浅入深，快速掌握AI应用技能',
    buttonText: '开始学习',
    imageType: 'video'
  },
  {
    key: 'custom',
    title: 'AI智能体+工作流',
    highlight: '定制',
    subtitle: '专注于为企业和个人提供定制解决方案',
    description: '使用AI提高工作效率，解决重复性工作，实现真正的AI生产力',
    buttonText: '我要定制',
    imageType: 'ai-circle'
  },
  {
    key: 'cases',
    title: '工作流',
    highlight: '案例',
    subtitle: '50+ 精选AI工作流案例，开放源码学习',
    description: '涵盖视频工作流，图片工作流，效率工具等，每个模板都经过精心测试和优化',
    buttonText: '浏览工作流',
    imageType: 'workflow-tree'
  }
]
</script>

<template>
  <div class="home">
    <!-- Hero Section with Carousel -->
    <section class="hero-section">
      <n-carousel 
        show-arrow 
        autoplay 
        draggable
        :interval="5000"
        :duration="800"
        easing="cubic-bezier(0.4, 0, 0.2, 1)"
        class="hero-carousel"
      >
        <n-carousel-item v-for="slide in carouselSlides" :key="slide.key">
          <div class="container hero-content">
            <div class="hero-text">
              <h1>
                {{ slide.title }} 
                <span class="highlight-box">{{ slide.highlight }}</span>
              </h1>
              <h2 class="subtitle">{{ slide.subtitle }}</h2>
              <p class="description">{{ slide.description }}</p>
              <button class="btn btn-primary btn-lg">{{ slide.buttonText }}</button>
            </div>
            
            <div class="hero-image">
              <!-- Slide 1: Course Card Stack Graphic -->
              <div v-if="slide.imageType === 'video'" class="course-graphic">
                <div class="course-card card-bg-1"></div>
                <div class="course-card card-bg-2"></div>
                <div class="course-card card-main">
                  <div class="card-header">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                  <div class="play-btn-container">
                    <div class="play-btn-inner">
                      <n-icon size="32" color="white">
                        <Play />
                      </n-icon>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Slide 2: AI Circle -->
              <div v-else-if="slide.imageType === 'ai-circle'" class="ai-graphic">
                <div class="ripple r1"></div>
                <div class="ripple r2"></div>
                <div class="ripple r3"></div>
                <div class="ai-core">AI</div>
              </div>

              <!-- Slide 3: Workflow Tree -->
              <div v-else-if="slide.imageType === 'workflow-tree'" class="workflow-graphic">
                <!-- SVG Lines -->
                <svg class="tree-lines" viewBox="0 0 300 250">
                  <!-- Connecting Lines (Background) -->
                  <g stroke="rgba(255, 102, 51, 0.2)" stroke-width="2" fill="none">
                    <path d="M150 40 L75 110" />
                    <path d="M150 40 L225 110" />
                    <path d="M150 40 L150 110" />
                    <path d="M75 110 L75 190" />
                    <path d="M225 110 L180 190" />
                    <path d="M150 110 L150 190" />
                  </g>
                  
                  <!-- Flowing Data (Animated) -->
                  <g stroke="#ff6b35" stroke-width="2" fill="none" class="flow-paths">
                    <path d="M150 40 L75 110" />
                    <path d="M150 40 L225 110" />
                    <path d="M150 40 L150 110" />
                    <path d="M75 110 L75 190" />
                    <path d="M225 110 L180 190" />
                    <path d="M150 110 L150 190" />
                  </g>
                </svg>

                <!-- Nodes with Icons -->
                <!-- Level 0: Root -->
                <div class="node-item root" style="top: 20px; left: 130px;">
                  <n-icon size="20" color="white"><GitNetworkOutline /></n-icon>
                </div>
                
                <!-- Level 1 -->
                <div class="node-item l1" style="top: 90px; left: 55px;">
                  <n-icon size="18" color="white"><CubeOutline /></n-icon>
                </div>
                <div class="node-item c1" style="top: 90px; left: 130px;">
                  <n-icon size="18" color="white"><CubeOutline /></n-icon>
                </div>
                <div class="node-item r1" style="top: 90px; left: 205px;">
                  <n-icon size="18" color="white"><CubeOutline /></n-icon>
                </div>
                
                <!-- Level 2 -->
                <div class="node-item l2" style="top: 170px; left: 55px;">
                  <n-icon size="16" color="white"><FlashOutline /></n-icon>
                </div>
                <div class="node-item c2" style="top: 170px; left: 130px;">
                  <n-icon size="16" color="white"><FlashOutline /></n-icon>
                </div>
                <div class="node-item r2" style="top: 170px; left: 160px;">
                  <n-icon size="16" color="white"><FlashOutline /></n-icon>
                </div>
              </div>
            </div>
          </div>
        </n-carousel-item>

        <!-- Custom Arrows -->
        <template #arrow="{ prev, next }">
          <div class="custom-arrow custom-arrow--left" @click="prev">
            <n-icon><ChevronBack /></n-icon>
          </div>
          <div class="custom-arrow custom-arrow--right" @click="next">
            <n-icon><ChevronForward /></n-icon>
          </div>
        </template>

        <!-- Custom Dots -->
        <template #dots="{ total, currentIndex, to }">
          <div class="custom-dots">
            <div
              v-for="index in total"
              :key="index"
              class="custom-dot"
              :class="{ 'is-active': currentIndex === index - 1 }"
              @click="to(index - 1)"
            />
          </div>
        </template>
      </n-carousel>
    </section>

    <!-- Products & Services -->
    <section class="section products-section">
      <div class="container">
        <h2 class="section-title">产品与服务</h2>
        <div class="underline"></div>
        
        <div class="grid-cards">
          <!-- Card 1 -->
          <div class="card product-card">
            <h3>专业课程</h3>
            <div class="card-list">
              <div class="list-item">COZE零基础入门课程</div>
              <div class="list-item">智能体/工作流拆解课程</div>
              <div class="list-item">一对一答疑服务</div>
            </div>
            <button class="btn btn-primary btn-block">查看课程</button>
          </div>

          <!-- Card 2 -->
          <div class="card product-card">
            <h3>工作流案例</h3>
            <div class="card-list">
              <div class="list-item">类型丰富的各种工作流</div>
              <div class="list-item">提供工作流源码学习参考</div>
              <div class="list-item">搭配专业课程，学习效果事半功倍</div>
            </div>
            <button class="btn btn-primary btn-block">查看案例</button>
          </div>

          <!-- Card 3 -->
          <div class="card product-card">
            <h3>智能体定制</h3>
            <div class="card-list">
              <div class="list-item">免费评估您的需求是否能通过AI来提高效率</div>
              <div class="list-item">不会为了定制而定制，不适合AI化的我们不会接</div>
              <div class="list-item">优惠的价格，专业的服务</div>
            </div>
            <button class="btn btn-primary btn-block">联系我们</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Why Choose Us -->
    <section class="section why-us-section">
      <div class="container">
        <h2 class="section-title">为什么选择我们</h2>
        <div class="underline"></div>

        <div class="grid-features">
          <div class="feature-item">
            <div class="icon-box">
              <n-icon size="40" color="#ff6b35">
                <RocketOutline />
              </n-icon>
            </div>
            <h3>技术专业</h3>
            <p>成员均是技术出身，有多年程序开发经验，AI工作流定制经验丰富</p>
          </div>
          
          <div class="feature-item">
            <div class="icon-box">
              <n-icon size="40" color="#ff6b35">
                <BookOutline />
              </n-icon>
            </div>
            <h3>服务贴心</h3>
            <p>非常好的服务态度，耐心细心贴心，沟通顺畅，方能合作愉快</p>
          </div>

          <div class="feature-item">
            <div class="icon-box">
              <n-icon size="40" color="#ff6b35">
                <PeopleOutline />
              </n-icon>
            </div>
            <h3>售后保障</h3>
            <p>提供售后服务，确保工作流正常运行</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Free Resources -->
    <section class="section resources-section">
      <div class="container">
        <h2 class="section-title">免费资源</h2>
        <div class="underline"></div>

        <div class="grid-cards">
          <div class="card resource-card">
            <h3>Coze零基础入门课程</h3>
            <p>从零开始，系统学习Coze平台使用</p>
            <a href="#" class="link-arrow">立即学习 →</a>
          </div>

          <div class="card resource-card">
            <h3>工作流案例</h3>
            <p>沉浸式历史故事、火柴人心理学等</p>
            <a href="#" class="link-arrow">查看案例 →</a>
          </div>

          <div class="card resource-card">
            <h3>学习交流群</h3>
            <p>加入社群，与同行交流经验</p>
            <a href="#" class="link-arrow">加入社群 →</a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* General Section Styles */
.section {
  padding: 60px 0;
}

.section-title {
  text-align: center;
  font-size: 32px;
  color: #333;
  margin-bottom: 8px;
}

.underline {
  width: 50px;
  height: 3px;
  background-color: var(--primary-color);
  margin: 0 auto 40px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF0E6 100%);
  min-height: 500px;
  position: relative;
}

.hero-carousel {
  height: 500px;
}

/* Custom Arrows */
.custom-arrow {
  display: flex;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: var(--primary-color);
  cursor: pointer;
  z-index: 10;
  transition: transform 0.2s;
}

.custom-arrow:hover {
  transform: translateY(-50%) scale(1.1);
}

.custom-arrow--left {
  left: 20px;
}

.custom-arrow--right {
  right: 20px;
}

/* Custom Dots */
.custom-dots {
  display: flex;
  gap: 10px;
  position: absolute;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
}

.custom-dot {
  width: 30px;
  height: 4px;
  background-color: rgba(255, 102, 51, 0.3);
  border-radius: 2px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.custom-dot.is-active {
  background-color: var(--primary-color);
}

.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  height: 100%;
  padding: 40px 80px 60px;
  max-width: 1100px;
  margin: 0 auto;
}

.hero-text {
  flex: 3;
}

.hero-text h1 {
  font-size: 48px;
  margin-bottom: 16px;
  font-weight: bold;
  line-height: 1.2;
  color: var(--primary-color);
}

.highlight-box {
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
  padding: 0 10px;
  border-radius: 8px;
  display: inline-block;
}

.subtitle {
  font-size: 22px;
  color: #333;
  margin-bottom: 16px;
  font-weight: bold;
}

.description {
  font-size: 16px;
  color: #666;
  margin-bottom: 32px;
  max-width: 600px;
  line-height: 1.6;
}

.btn-lg {
  padding: 12px 36px;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(255, 102, 51, 0.3);
}

.hero-image {
  flex: 2;
  display: flex;
  justify-content: flex-end;
  height: 300px;
  align-items: center;
  position: relative;
}

/* Graphics */
.course-graphic {
  width: 320px;
  height: 240px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.course-card {
  position: absolute;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(255, 102, 51, 0.15);
  transition: all 0.5s ease;
}

.card-bg-1 {
  width: 260px;
  height: 160px;
  background: rgba(255, 102, 51, 0.15);
  transform: rotate(-8deg) translate(-15px, 15px);
  z-index: 1;
  animation: float-bg-1 6s ease-in-out infinite;
}

.card-bg-2 {
  width: 270px;
  height: 170px;
  background: rgba(255, 102, 51, 0.3);
  transform: rotate(5deg) translate(15px, -5px);
  z-index: 2;
  animation: float-bg-2 7s ease-in-out infinite;
}

.card-main {
  width: 280px;
  height: 180px;
  background: white;
  z-index: 3;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 102, 51, 0.1);
  animation: float-main 5s ease-in-out infinite;
}

.card-header {
  height: 28px;
  background: rgba(255, 102, 51, 0.08);
  display: flex;
  align-items: center;
  padding: 0 12px;
  gap: 6px;
  border-bottom: 1px solid rgba(255, 102, 51, 0.05);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 102, 51, 0.4);
}

.play-btn-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, rgba(255, 102, 51, 0.05) 0%, transparent 70%);
}

.play-btn-inner {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-left: 4px;
  box-shadow: 0 8px 20px rgba(255, 102, 51, 0.4);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.play-btn-inner:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 25px rgba(255, 102, 51, 0.5);
}

@keyframes float-main {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes float-bg-1 {
  0%, 100% { transform: rotate(-8deg) translate(-15px, 15px); }
  50% { transform: rotate(-6deg) translate(-15px, 10px); }
}

@keyframes float-bg-2 {
  0%, 100% { transform: rotate(5deg) translate(15px, -5px); }
  50% { transform: rotate(4deg) translate(15px, 0px); }
}

/* AI Circle Graphic */
.ai-graphic {
  width: 300px;
  height: 300px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-core {
  width: 100px;
  height: 100px;
  background: var(--primary-color);
  border-radius: 50%;
  color: white;
  font-size: 32px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
  box-shadow: 0 4px 20px rgba(255, 102, 51, 0.4);
  animation: float 4s ease-in-out infinite;
}

.ripple {
  position: absolute;
  border: 1px solid rgba(255, 102, 51, 0.2);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: ripple 3s infinite linear;
}

.r1 { width: 160px; height: 160px; border-width: 1px; }
.r2 { width: 220px; height: 220px; border-width: 1px; opacity: 0.6; }
.r3 { width: 280px; height: 280px; border-width: 1px; opacity: 0.3; }

/* Workflow Graphic */
.workflow-graphic {
  width: 300px;
  height: 250px;
  position: relative;
  animation: float 6s ease-in-out infinite; /* Added floating effect */
}

.tree-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.flow-paths path {
  stroke-dasharray: 10 100;
  stroke-dashoffset: 110;
  animation: flow-line 1.5s linear infinite;
  opacity: 0.8;
}

.node-item {
  position: absolute;
  width: 40px;
  height: 40px;
  background-color: var(--primary-color);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 102, 51, 0.4);
  z-index: 2;
  transition: transform 0.3s;
}

.node-item.root {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  animation: pulse-node 3s infinite;
}

.node-item.l1, .node-item.c1, .node-item.r1 {
  animation: pulse-node 3s infinite 0.5s;
}

.node-item.l2, .node-item.c2, .node-item.r2 {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  animation: pulse-node 3s infinite 1s;
}

@keyframes flow-line {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes pulse-node {
  0%, 100% { transform: scale(1); box-shadow: 0 4px 12px rgba(255, 102, 51, 0.4); }
  50% { transform: scale(1.1); box-shadow: 0 8px 20px rgba(255, 102, 51, 0.6); }
}


/* Products Section */
.products-section {
  background-color: #FFFBF9;
}

.grid-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

.card {
  background: #fff;
  border-radius: 12px;
  padding: 30px 24px;
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  flex-direction: column;
}

.product-card {
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.product-card h3 {
  text-align: center;
  font-size: 22px;
  margin-bottom: 20px;
  color: #333;
}

.card-list {
  flex: 1;
  margin-bottom: 24px;
}

.list-item {
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
  color: #666;
  font-size: 14px;
}

.list-item:last-child {
  border-bottom: none;
}

.btn-block {
  width: 100%;
}

/* Why Us Section */
.why-us-section {
  background-color: #FFF5EF;
}

.grid-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  text-align: center;
}

.feature-item {
  background: #fff;
  padding: 30px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #eee;
  transition: transform 0.3s, box-shadow 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border-color: var(--primary-color);
}

.icon-box {
  width: 64px;
  height: 64px;
  background-color: var(--bg-secondary);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  transition: background-color 0.3s;
}

.feature-item:hover .icon-box {
  background-color: #FFE0D6; /* Slightly darker orange tint on hover */
}

.feature-item h3 {
  font-size: 18px;
  margin-bottom: 12px;
  font-weight: bold;
  color: #333;
}

.feature-item p {
  color: #666;
  line-height: 1.6;
  flex: 1;
}

/* Resources Section */
.resources-section {
  background-color: #FFFFFF;
}

.resource-card {
  background-color: #fff;
  border: 1px solid #eee; /* Added border */
  align-items: flex-start;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Added shadow */
  transition: transform 0.3s, box-shadow 0.3s;
}

.resource-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  border-color: var(--primary-color);
}

.resource-card h3 {
  font-size: 18px;
  margin-bottom: 10px;
  font-weight: bold;
}

.resource-card p {
  color: #888;
  font-size: 14px;
  margin-bottom: 16px;
  flex: 1;
}

.link-arrow {
  color: var(--primary-color);
  font-weight: bold;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: gap 0.3s;
}

.link-arrow:hover {
  gap: 10px;
}

/* Responsive Design */
@media (max-width: 992px) {
  .hero-content {
    flex-direction: column-reverse; /* Stack image on top of text */
    text-align: center;
    justify-content: center; /* Center content vertically if needed */
  }

  .hero-text {
    margin-bottom: 20px;
    width: 100%;
    flex: unset; /* Reset flex shrink/grow */
  }
  
  .description {
    margin-left: auto;
    margin-right: auto;
  }
  
  .hero-image {
    width: 100%;
    height: auto;
    min-height: 250px;
    justify-content: center; /* Center image horizontally */
    flex: unset; /* Reset flex shrink/grow */
    margin-bottom: 30px; /* Add spacing between image and text */
  }
  
  .hero-carousel {
    height: auto;
    min-height: 600px;
  }

  .custom-arrow {
    display: none; /* Hide arrows on smaller screens usually, or adjust position */
  }

  .grid-cards, .grid-features {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .hero-text h1 {
    font-size: 32px;
  }

  .subtitle {
    font-size: 18px;
  }

  .grid-cards, .grid-features {
    grid-template-columns: 1fr;
  }
  
  .section {
    padding: 50px 0;
  }
  
  /* Mobile optimizations requested */
  .hero-section {
    min-height: auto;
  }

  /* Ensure hero image is visible and centered on mobile */
  .hero-image {
    display: flex; 
    margin-bottom: 0; /* Reduced from 20px */
    min-height: 180px; /* Reduced height */
  }

  /* Scale down graphics for mobile */
  .course-graphic, .ai-graphic, .workflow-graphic {
    transform: scale(0.75);
    width: auto; 
    height: auto;
    min-height: 220px; 
    min-width: 280px;
    margin: -30px 0; /* Negative margin to offset scale whitespace */
  }

  .hero-content {
    padding: 40px 20px 60px; /* Restore top padding */
    flex-direction: column; /* Text on top, image below */
  }

  .hero-text {
    margin-bottom: 0;
  }

  .hero-carousel {
    height: auto;
    min-height: unset;
  }

  /* Ensure dots are visible on mobile */
  .custom-dots {
    display: flex;
  }
}
</style>
