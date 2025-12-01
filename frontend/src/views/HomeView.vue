<script setup>
import { RocketOutline, BookOutline, PeopleOutline, ChevronBack, ChevronForward } from '@vicons/ionicons5'
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
              <!-- Slide 1: Video Placeholder -->
              <div v-if="slide.imageType === 'video'" class="video-placeholder">
                <div class="play-icon">▶</div>
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
                  <!-- Top to Mid -->
                  <line x1="150" y1="30" x2="75" y2="100" stroke="#FF6633" stroke-width="2" />
                  <line x1="150" y1="30" x2="225" y2="100" stroke="#FF6633" stroke-width="2" />
                  <line x1="150" y1="30" x2="150" y2="100" stroke="#FF6633" stroke-width="2" />
                  
                  <!-- Mid to Bottom -->
                  <line x1="75" y1="100" x2="75" y2="180" stroke="#FF6633" stroke-width="2" />
                  <line x1="225" y1="100" x2="180" y2="180" stroke="#FF6633" stroke-width="2" />
                  <line x1="150" y1="100" x2="150" y2="180" stroke="#FF6633" stroke-width="2" />
                </svg>

                <!-- Nodes -->
                <div class="node root" style="top: 10px; left: 130px;"></div>
                
                <div class="node l1" style="top: 90px; left: 55px;"></div>
                <div class="node c1" style="top: 90px; left: 130px;"></div>
                <div class="node r1" style="top: 90px; left: 205px;"></div>
                
                <div class="node l2" style="top: 170px; left: 55px;"></div>
                <div class="node c2" style="top: 170px; left: 130px;"></div>
                <div class="node r2" style="top: 170px; left: 160px;"></div>
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
              <n-icon size="40" color="#FF6633">
                <RocketOutline />
              </n-icon>
            </div>
            <h3>技术专业</h3>
            <p>成员均是技术出身，有多年程序开发经验，AI工作流定制经验丰富</p>
          </div>
          
          <div class="feature-item">
            <div class="icon-box">
              <n-icon size="40" color="#FF6633">
                <BookOutline />
              </n-icon>
            </div>
            <h3>服务贴心</h3>
            <p>非常好的服务态度，耐心细心贴心，沟通顺畅，方能合作愉快</p>
          </div>

          <div class="feature-item">
            <div class="icon-box">
              <n-icon size="40" color="#FF6633">
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
  background-color: var(--bg-secondary);
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
.video-placeholder {
  width: 100%;
  max-width: 380px;
  aspect-ratio: 16/9;
  background: linear-gradient(135deg, #fff 0%, #FFF5F0 100%);
  border: none;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 40px rgba(255, 102, 51, 0.15), 0 0 0 1px rgba(255, 102, 51, 0.1);
  animation: float 6s ease-in-out infinite;
  position: relative;
  overflow: hidden;
}

/* Add a decorative course card look */
.video-placeholder::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 6px;
  background: var(--primary-color);
}

.play-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #FF8855, #FF6633);
  border-radius: 50%;
  color: white;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-left: 4px;
  animation: pulse 2s infinite;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 8px 20px rgba(255, 102, 51, 0.4);
  z-index: 2;
}

.play-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 25px rgba(255, 102, 51, 0.5);
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
  background: linear-gradient(135deg, #FF8855, #FF6633);
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
  background-color: #FFF5F0; /* Match bg to blend, or use white circle */
  background: radial-gradient(circle, #fff 0%, #FFF5F0 70%); /* Subtle glow */
  border-radius: 50%; /* Optional container shape */
}

.tree-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.tree-lines line {
  stroke-dasharray: 100;
  stroke-dashoffset: 100;
  animation: drawLines 2s ease-out forwards;
}

.node {
  position: absolute;
  width: 40px;
  height: 28px;
  background-color: var(--primary-color);
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(255, 102, 51, 0.3);
  opacity: 0;
  animation: popIn 0.5s ease-out forwards;
}

.node.root { animation-delay: 0.5s; }
.node.l1, .node.c1, .node.r1 { animation-delay: 1s; }
.node.l2, .node.c2, .node.r2 { animation-delay: 1.5s; }

.node::after {
  content: '';
  display: block;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  margin: 10px auto;
}

/* Keyframes */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255, 102, 51, 0.7); }
  70% { box-shadow: 0 0 0 15px rgba(255, 102, 51, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 102, 51, 0); }
}

@keyframes ripple {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

@keyframes drawLines {
  to { stroke-dashoffset: 0; }
}

@keyframes popIn {
  from { transform: scale(0); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* Products Section */
.products-section {
  background-color: #FEEFED;
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
  background-color: #FFF8F2;
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
  background-color: #FDF2EE;
}

.resource-card {
  background-color: #fff;
  border: none;
  align-items: flex-start;
  padding: 24px;
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
    flex-direction: column;
    text-align: center;
  }

  .hero-text {
    margin-bottom: 20px;
    width: 100%;
  }
  
  .description {
    margin-left: auto;
    margin-right: auto;
  }
  
  .hero-image {
    width: 100%;
    height: auto;
    min-height: 250px;
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

  .hero-image {
    display: none;
  }

  .hero-content {
    padding-bottom: 40px;
    justify-content: center;
    text-align: center;
  }

  .hero-text {
    margin-bottom: 0;
  }

  .hero-carousel {
    height: auto;
    min-height: unset;
  }
}
</style>
