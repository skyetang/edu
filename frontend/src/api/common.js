import request from '@/utils/request'

// 获取VOD上传签名
export function getVodSignature() {
  return request({
    url: '/common/vod/signature/',
    method: 'get',
    params: {
      type: 'upload'
    }
  })
}

// 获取VOD播放签名
export function getVodPlaySignature(fileId) {
  return request({
    url: '/common/vod/signature/',
    method: 'get',
    params: {
      type: 'play',
      file_id: fileId
    }
  })
}

// 通用文件上传 (支持 type 参数: avatar, course_cover, category_cover, material, etc.)
export function uploadFile(formData, type = 'file') {
  return request({
    url: '/common/upload/file/',
    method: 'post',
    data: formData,
    params: { type },
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
