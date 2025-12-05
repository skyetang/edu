# 课程管理模块需求与技术方案对齐 (Alignment) v3

## 1. 需求概述
构建课程管理系统，核心围绕“会员权益”展开。视频点播（VOD）与对象存储（COS）采用不同的集成策略。

### 1.1 核心业务规则
1.  **权益模式**：仅支持会员权益免费看，不支持单买。
2.  **数据策略**：不记录学习进度；删除时仅删数据库记录，保留云端文件。

## 2. 架构设计调整 (Final)

### 2.1 腾讯云服务集成策略
- **VOD (视频)**: **前端直传**。
  - 后端仅负责生成“上传签名” (Signature)。
  - 前端拿到签名后调用 VOD SDK 上传，成功后将 `fileId` 传给后端保存。
  
- **COS (图片/附件)**: **后端代理上传** (根据最新反馈调整)。
  - **流程**：前端将文件（如封面图）通过 `Multipart/Form-Data` 发送给后端接口 -> 后端接收文件流 -> 后端调用 COS SDK 上传到腾讯云 -> 后端获取 URL 并保存/返回。
  - **理由**：简化前端逻辑，便于后端控制图片处理、重命名和目录结构。

### 2.2 模块划分
- `apps.common`:
  - `services/cos.py`: 封装 COS 上传逻辑 (Backend Upload)。
  - `services/vod.py`: 封装 VOD 签名生成逻辑。
  - 接口：
    - `POST /api/common/upload/image/`: 接收文件 -> 上传 COS -> 返回 URL。
    - `GET /api/common/vod/signature/`: 返回 VOD 上传签名。

- `apps.courses`:
  - 负责课程、分类、章节、课时的业务逻辑。

## 3. 依赖包
- `tencentcloud-sdk-python` (VOD 签名, 通用 API)
- `cos-python-sdk-v5` (COS 上传操作)

## 4. 接口设计规划 (apps.common)

### 4.1 图片上传 (后端上传模式)
- **URL**: `POST /api/common/upload/image/`
- **权限**: `IsAuthenticated` & `IsAdminUser` (仅管理后台可用)
- **参数**: `file` (Form Data)
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "url": "https://bucket.cos.region.myqcloud.com/path/to/image.jpg"
    }
  }
  ```

### 4.2 VOD 签名 (前端上传模式)
- **URL**: `GET /api/common/vod/signature/`
- **权限**: `IsAuthenticated` & `IsAdminUser`
- **响应**:
  ```json
  {
    "success": true,
    "data": {
      "signature": "xD3..."
    }
  }
  ```
