# 认证模块接口文档

本文档描述了用户注册、登录及短信验证码相关的 API 接口。

## 1. 统一响应结构

所有接口均遵循以下统一响应格式：

```json
{
  "success": true, // true 表示业务成功，false 表示失败
  "code": "OK", // 业务状态码，如 OK, VALIDATION_ERROR, CONFLICT 等
  "message": "ok", // 提示信息
  "data": {}, // 业务数据
  "meta": null, // 元数据（如分页信息）
  "request_id": "uuid..." // 请求追踪 ID
}
```

常见错误码：
- `OK`: 成功
- `VALIDATION_ERROR`: 参数校验失败 (HTTP 422)
- `CONFLICT`: 资源冲突（如手机号已存在） (HTTP 409)
- `RATE_LIMITED`: 请求过于频繁 (HTTP 429)
- `AUTH_EXPIRED`: 认证失败或过期 (HTTP 401)
- `NOT_FOUND`: 资源不存在 (HTTP 404)

---

## 2. 接口详情

### 2.1 发送短信验证码

- **URL**: `/api/auth/send_code`
- **Method**: `POST`
- **Auth**: 无需认证
- **Description**: 发送短信验证码，用于注册或登录。

**请求参数 (JSON)**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `phone` | string | 是 | 手机号码 |
| `scene` | string | 是 | 场景：`register` (注册) 或 `login` (登录) |

**请求示例**

```json
{
  "phone": "13800138000",
  "scene": "register"
}
```

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "sent": true
  }
}
```

**响应示例 (失败 - 手机号已注册)**

```json
{
  "success": false,
  "code": "CONFLICT",
  "message": "手机号已注册"
}
```

**响应示例 (失败 - 频率限制)**

```json
{
  "success": false,
  "code": "RATE_LIMITED",
  "message": "请求过于频繁"
}
```

---

### 2.2 用户注册

- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Auth**: 无需认证
- **Description**: 使用手机号、验证码和密码进行注册。注册成功后自动颁发 Token。

**请求参数 (JSON)**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `phone` | string | 是 | 手机号码 |
| `code` | string | 是 | 短信验证码 (6位) |
| `password` | string | 是 | 密码 (至少6位) |

**请求示例**

```json
{
  "phone": "13800138000",
  "code": "123456",
  "password": "securepassword123"
}
```

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "phone": "13800138000"
    }
  }
}
```

**响应示例 (失败 - 验证码无效)**

```json
{
  "success": false,
  "code": "VALIDATION_ERROR",
  "message": "验证码无效"
}
```

---

### 2.3 密码登录

- **URL**: `/api/auth/login/password`
- **Method**: `POST`
- **Auth**: 无需认证
- **Description**: 使用手机号和密码登录。

**请求参数 (JSON)**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `phone` | string | 是 | 手机号码 |
| `password` | string | 是 | 密码 |

**请求示例**

```json
{
  "phone": "13800138000",
  "password": "securepassword123"
}
```

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "phone": "13800138000"
    }
  }
}
```

**响应示例 (失败 - 用户不存在)**

```json
{
  "success": false,
  "code": "NOT_FOUND",
  "message": "用户不存在"
}
```

**响应示例 (失败 - 密码错误)**

```json
{
  "success": false,
  "code": "AUTH_EXPIRED",
  "message": "认证失败"
}
```

---

### 2.4 验证码登录

- **URL**: `/api/auth/login/code`
- **Method**: `POST`
- **Auth**: 无需认证
- **Description**: 使用手机号和短信验证码登录。如果手机号不存在，将自动创建新用户。

**请求参数 (JSON)**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `phone` | string | 是 | 手机号码 |
| `code` | string | 是 | 短信验证码 (6位) |

**请求示例**

```json
{
  "phone": "13800138000",
  "code": "123456"
}
```

**响应示例 (成功)**

```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "phone": "13800138000"
    }
  }
}
```
