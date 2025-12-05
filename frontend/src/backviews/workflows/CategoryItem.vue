<template>
  <div class="category-item-container" :class="{ 'is-root-container': level === 0 }">
    <!-- 当前分类行 -->
    <div class="category-row" :class="{ 'is-root': level === 0 }">
      <div class="row-content">
        <!-- 展开/收起图标 (仅一级分类显示) -->
        <div 
          v-if="level === 0"
          class="expand-icon" 
          @click="toggleExpand"
          :class="{ 'is-hidden': !hasChildren && !alwaysShowExpand }"
        >
          <n-icon :component="isExpanded ? ChevronDown : ChevronForward" v-if="hasChildren || alwaysShowExpand" />
        </div>

        <!-- 封面图 -->
        <div class="category-cover size-large">
          <img v-if="data.cover || data.image" :src="data.cover || data.image" alt="cover" />
          <div v-else class="no-cover">
            <n-icon :component="ImageOutline" />
          </div>
        </div>

        <!-- 名称 -->
        <div class="category-name text-large">{{ data.name }}</div>
        
        <!-- 描述 (可选) -->
        <div class="category-desc" v-if="data.description">{{ data.description }}</div>

        <!-- 操作按钮 -->
        <div class="row-actions">
          <n-button text type="primary" size="small" @click="$emit('edit', data)">编辑</n-button>
          <n-divider vertical />
          <n-button text type="error" size="small" @click="$emit('delete', data)">删除</n-button>
        </div>
      </div>
    </div>

    <!-- 子分类列表 -->
    <n-collapse-transition :show="isExpanded">
      <div class="children-container" v-if="level === 0">
        <CategoryItem
          v-for="child in data.children"
          :key="child.id"
          :data="child"
          :level="level + 1"
          :always-show-expand="alwaysShowExpand"
          @add-sub="$emit('add-sub', $event)"
          @edit="$emit('edit', $event)"
          @delete="$emit('delete', $event)"
        />
        
        <!-- 添加子类按钮 (作为列表最后以一项) -->
        <div class="add-sub-row" v-if="level < 1">
          <n-button class="add-sub-btn" dashed size="small" @click="$emit('add-sub', data)">
            <template #icon><n-icon :component="Add" /></template>
            添加子分类
          </n-button>
        </div>
      </div>
    </n-collapse-transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { NIcon, NButton, NCollapseTransition, NDivider } from 'naive-ui'
import { ChevronForward, ChevronDown, ImageOutline, Add } from '@vicons/ionicons5'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  alwaysShowExpand: {
    type: Boolean,
    default: false
  }
})

defineEmits(['add-sub', 'edit', 'delete'])

const isExpanded = ref(true)

const hasChildren = computed(() => {
  return props.data.children && props.data.children.length > 0
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
.category-item-container {
  width: 100%;
}

.category-item-container.is-root-container {
  margin-bottom: 16px;
  border: 1px solid #efeff5;
  border-radius: 8px;
}

.category-item-container.is-root-container:last-child {
  margin-bottom: 0;
}

.category-row {
  padding: 12px 16px;
  transition: background-color 0.2s;
  border-radius: 8px;
}

.category-row:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.category-row.is-root {
  background-color: #fff;
  padding-top: 16px;
  padding-bottom: 16px;
}

.category-row:not(.is-root) {
  background-color: transparent;
  padding: 8px 12px;
}

.category-row:not(.is-root):hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.children-container {
  margin-top: 0;
  margin-left: 102px; /* Align with Level 0 Title: 16(pad)+24(arrow)+16(gap)+72(cover)+16(gap) - 12(childPad) */
  margin-right: 16px;
  margin-bottom: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 8px;
}

.row-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.expand-icon {
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  transition: color 0.2s;
  flex-shrink: 0;
}

.expand-icon:hover {
  color: #333;
}

.expand-icon.is-hidden {
  visibility: hidden;
}

.category-cover {
  border-radius: 6px;
  overflow: hidden;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #eee;
  flex-shrink: 0;
}

.category-cover.size-large {
  width: 72px;
  height: 54px; /* 4:3 ratio */
}

/* Removed size-small as it is no longer used */

.category-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-cover {
  color: #ccc;
  font-size: 20px;
}

.category-name {
  color: #333;
}

.category-name.text-large {
  font-weight: 600;
  font-size: 16px;
  color: #1f2225;
}

/* Removed text-small as it is no longer used */

.category-desc {
  color: #999;
  font-size: 13px;
  margin-left: 8px;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.category-row:hover .row-actions {
  opacity: 1;
}

.add-sub-row {
  padding: 8px 12px;
  background-color: transparent;
  display: flex;
  justify-content: flex-start;
}

.add-sub-btn {
  padding-left: 0;
}
</style>