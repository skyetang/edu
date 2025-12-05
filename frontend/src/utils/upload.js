/** 
 * 腾讯云视频上传工具 
 * 使用腾讯云 vod-js-sdk-v6 上传视频和封面 
 */ 

import TcVod from 'vod-js-sdk-v6' 

// 签名缓存 
let signatureCache = null 
let signatureCacheTime = 0 
const SIGNATURE_CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存 

/** 
 * 创建腾讯云上传器，带签名缓存 
 * @param {Function} getSignature - 获取签名的函数 
 * @returns {TcVod} 腾讯云上传器实例 
 */ 
export const createUploader = (getSignature) => { 
  // 包装 getSignature 函数，添加缓存逻辑 
  const getSignatureWithCache = async () => { 
    const now = Date.now() 

    // 检查缓存是否有效 
    if (signatureCache && (now - signatureCacheTime) < SIGNATURE_CACHE_DURATION) { 
      return signatureCache 
    } 

    try { 
      const signature = await getSignature() 

      if (!signature) { 
        throw new Error('签名为空') 
      } 

      signatureCache = signature 
      signatureCacheTime = now 
      return signature 
    } catch (error) { 
      throw new Error('获取腾讯云签名失败: ' + error.message) 
    } 
  } 

  return new TcVod({ 
    getSignature: getSignatureWithCache 
  }) 
} 

/** 
 * 上传视频和封面 
 * @param {File} mediaFile - 视频文件（可选，只更新封面时可为 null） 
 * @param {File} coverFile - 封面文件（可选） 
 * @param {Function} getSignature - 获取签名的函数 
 * @param {Function} onMediaProgress - 视频上传进度回调 
 * @param {Function} onCoverProgress - 封面上传进度回调 
 * @param {string} fileId - 文件 ID（可选，只更新封面时需要传递） 
 * @returns {Promise} 返回上传结果 { fileId, video: { url }, cover: { url } } 
 */ 
export const uploadMediaFiles = async ( 
  mediaFile, 
  coverFile, 
  getSignature, 
  onMediaProgress, 
  onCoverProgress, 
  fileId = null 
) => { 
  try { 
    // 如果没有视频文件，则必须提供 fileId（只更新封面的情况） 
    if (!mediaFile && !fileId) { 
      throw new Error('视频文件和文件 ID 不能同时为空') 
    } 

    const tcVod = createUploader(getSignature) 

    // 构建上传配置 
    const uploadConfig = { 
      mediaFile: mediaFile, 
      coverFile: coverFile 
    } 

    // 如果提供了 fileId，则添加到配置中（用于只更新封面的情况） 
    if (fileId) { 
      uploadConfig.fileId = fileId 
    } 

    const uploader = tcVod.upload(uploadConfig) 

    // 监听视频上传进度 
    if (onMediaProgress) { 
      uploader.on('media_progress', (info) => { 
        onMediaProgress(info) 
      }) 
    } 

    // 监听视频上传完成 
    uploader.on('media_upload', (info) => { 
      // 视频上传完成 
    }) 

    // 监听封面上传进度 
    if (onCoverProgress) { 
      uploader.on('cover_progress', (info) => { 
        onCoverProgress(info) 
      }) 
    } 

    // 监听封面上传完成 
    uploader.on('cover_upload', (info) => { 
      // 封面上传完成 
    }) 

    // 等待上传完成 
    const result = await uploader.done() 

    return result 
  } catch (error) { 
    throw new Error('上传文件失败: ' + (error.message || error)) 
  } 
} 

/** 
 * 从上传结果中提取必要的信息 
 * @param {Object} doneResult - 腾讯云上传完成结果 
 * @returns {Object} 提取的信息 { fileId, mediaUrl, coverUrl } 
 */ 
export const extractUploadInfo = (doneResult) => { 
  if (!doneResult) { 
    return { 
      fileId: '', 
      mediaUrl: '', 
      coverUrl: '' 
    } 
  } 

  // 根据腾讯云VOD SDK v6返回结构提取
  // 结构示例:
  // {
  //   fileId: "5145403707872456048",
  //   video: { url: "https://...", verify_content: "..." },
  //   cover: { url: "https://...", verify_content: "..." }
  // }
  const uploadInfo = { 
    fileId: doneResult.fileId || '', 
    mediaUrl: doneResult.video?.url || '', 
    coverUrl: doneResult.cover?.url || '' 
  } 

  return uploadInfo 
}