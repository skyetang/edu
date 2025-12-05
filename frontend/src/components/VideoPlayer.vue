<template>
  <div class="player-wrapper">
    <video id="player-container" class="player-container" preload="auto" playsinline webkit-playsinline></video>
  </div>
</template>

<script setup name="VideoPlayer">
import { onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useDialog } from 'naive-ui'
import TCPlayer from 'tcplayer.js'
import 'tcplayer.js/dist/tcplayer.min.css'

const dialog = useDialog()
const props = defineProps({
  fileId: {
    type: String,
    required: true
  },
  signature: {
    type: String,
    required: true
  },
  appId: {
    type: String,
    required: true
  },
  licenseUrl: {
    type: String,
    default: ''
  },
  prevLesson: Object,
  currentLesson: Object,
  nextLesson: Object
})

const emits = defineEmits(['switch'])

let player = null

// 处理视频播放完成
const handlePlayComplete = () => {
  if (props.nextLesson) {
    dialog.warning({
      title: '下一课时',
      content: `即将播放：${props.nextLesson.title}`,
      positiveText: '继续学习',
      negativeText: '重新观看',
      onPositiveClick: () => {
        emits('switch', props.nextLesson.id)
      },
      onNegativeClick: () => {
        if (player) {
          player.currentTime(0)
          player.play()
        }
      }
    })
  } else {
    dialog.success({
      title: '课程完成',
      content: '恭喜您，您已学完本课程！',
      positiveText: '重新观看',
      onPositiveClick: () => {
        if (player) {
          player.currentTime(0)
          player.play()
        }
      }
    })
  }
}

// 初始化播放器
const initPlayer = () => {
  if (!props.fileId || !props.signature) {
    return
  }

  // 如果已存在实例，先销毁
  if (player) {
    player.dispose()
    player = null
  }

  // 检查播放器容器元素是否存在，如果不存在则重新创建（防止dispose后元素被移除）
  let videoEl = document.getElementById('player-container')
  if (!videoEl) {
    const wrapper = document.querySelector('.player-wrapper')
    if (wrapper) {
      videoEl = document.createElement('video')
      videoEl.id = 'player-container'
      videoEl.className = 'player-container'
      videoEl.preload = 'auto'
      videoEl.setAttribute('playsinline', 'true')
      videoEl.setAttribute('webkit-playsinline', 'true')
      wrapper.appendChild(videoEl)
    }
  }

  try {
    const options = {
      fileID: props.fileId,
      appID: props.appId,
      psign: props.signature,
      licenseUrl: props.licenseUrl,
      autoplay: true,
      controls: true,
      preload: 'auto',
      hlsConfig: {
        enableWorker: true,
        debug: false
      },
      plugins: {
        ContinuePlay: { // 开启续播功能
          auto: true
        }
      }
    }
    player = TCPlayer('player-container', options)

    // 监听视频播放完成事件
    player.on('ended', handlePlayComplete)
  } catch (error) {
    console.error('播放器初始化失败:', error)
  }
}

// 监听参数变化
watch(
  () => [props.fileId, props.signature],
  async ([newFileId, newSignature]) => {
    if (!newFileId || !newSignature) return

    if (player) {
      try {
        // 移除旧的事件监听
        player.off('ended', handlePlayComplete)
        
        // TCPlayer v4+ loadVideoByID
        player.loadVideoByID({
          fileID: newFileId,
          appID: props.appId,
          psign: newSignature
        })
        
        // 添加新的事件监听
        player.on('ended', handlePlayComplete)
      } catch (error) {
        console.error('切换视频失败:', error)
        // 如果切换失败，重新初始化播放器
        player.dispose()
        player = null
        await nextTick()
        initPlayer()
      }
    } else {
      await nextTick()
      initPlayer()
    }
  }
)

onMounted(() => {
  // 确保有必要的参数才初始化播放器
  if (props.fileId && props.signature) {
    initPlayer()
  }
})

onUnmounted(() => {
  if (player) {
    player.off('ended', handlePlayComplete)
    player.dispose()
    player = null
  }
})
</script>

<style scoped>
.player-wrapper {
  width: 100%;
  height: 100%;
  background-color: #000;
}

.player-container {
  width: 100%;
  height: 100%;
}

/* Force 16:9 Aspect Ratio for TCPlayer container */
:deep(.tcp-player-container) {
  padding-top: 56.25% !important; /* 16:9 Aspect Ratio */
}
</style>