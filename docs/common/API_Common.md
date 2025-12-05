# 公共服务接口文档

本文档描述了文件上传（COS）与视频点播（VOD）相关的 API 接口。

## 1. 统一响应结构

所有接口均遵循以下统一响应格式：

```json
{
  "success": true, // true 表示业务成功，false 表示失败
  "code": "OK", // 业务状态码，如 OK, VALIDATION_ERROR, SERVER_ERROR 等
  "message": "ok", // 提示信息
  "data": {}, // 业务数据
  "meta": null, // 元数据
  "request_id": "uuid..." // 请求追踪 ID
}
```

常见错误码：
- `OK`: 成功
- `VALIDATION_ERROR`: 参数校验失败 (HTTP 422)
- `SERVER_ERROR`: 服务器内部错误 (HTTP 500)
- `AUTH_EXPIRED`: 认证失败或过期 (HTTP 401)
- `PERMISSION_DENIED`: 权限不足 (HTTP 403)

---

## 2. 接口详情

### 2.1 通用文件上传 (COS)

- **URL**: `/api/common/upload/file/`
- **Method**: `POST`
- **Auth**: 需要认证 (Bearer Token)
- **Description**: 上传文件（图片、文档、压缩包等）到腾讯云 COS，并根据 `type` 参数自动存储到对应目录。

**请求参数 (Query Param)**

| 字段名 | 类型 | 必选 | 默认值 | 描述 |
| :--- | :--- | :--- | :--- | :--- |
| `type` | string | 否 | `image` | 上传类型，决定存储路径 |

**`type` 可选值及对应路径：**
- `image` -> `images/` (默认)
- `avatar` -> `avatars/` (用户头像)
- `course_cover` -> `courses/covers/` (课程封面)
- `category_cover` -> `categories/covers/` (分类封面)
- `material` -> `materials/` (课程资料，如 pdf/zip)
- `document` -> `documents/`
- `file` -> `files/`

**请求参数 (Form-Data)**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `file` | file | 是 | 文件对象 (支持 jpg, png, pdf, zip 等) |

**请求示例**

```bash
# 上传课程封面
curl -X POST "http://localhost:8000/api/common/upload/file/?type=course_cover" \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/to/cover.jpg"
```

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "url": "https://example-bucket.cos.ap-guangzhou.myqcloud.com/courses/covers/uuid.jpg"
  },
  "request_id": "..."
}
```

**响应示例 (失败 - 无文件)**

```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "未找到文件",
  "request_id": "..."
}
```

---

### 2.2 获取 VOD 上传签名

- **URL**: `/api/common/vod/signature/`
- **Method**: `GET`
- **Auth**: 需要认证 (Bearer Token)
- **Description**: 获取腾讯云点播（VOD）的前端上传签名。前端使用此签名调用 VOD SDK 上传视频。

**请求参数**

无

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "获取签名成功",
  "data": {
    "signature": "eHxdfdf..." // Base64 编码的签名字符串
  },
  "request_id": "..."
}
```
