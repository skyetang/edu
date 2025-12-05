# 课程管理模块接口文档

本文档描述了课程分类、课程管理、章节课时管理以及客户端课程展示相关的 API 接口。

## 1. 统一响应结构

所有接口均遵循项目统一响应格式。

## 2. 管理端接口 (Admin)

**权限要求**: 需要管理员权限 (is_staff=True)

### 2.1 课程分类管理

**基础路径**: `/api/courses/categories/`

#### 2.1.1 获取分类列表 (树形结构)

- **URL**: `/api/courses/categories/`
- **Method**: `GET`
- **Description**: 获取所有课程分类，返回递归树形结构。

**响应示例**

```json
{
  "success": true,
  "code": "OK",
  "data": [
    {
      "id": 1,
      "name": "前端开发",
      "parent": null,
      "sort_order": 0,
      "image": "http://...",
      "description": "...",
      "children": [
        {
          "id": 2,
          "name": "Vue.js",
          "parent": 1,
          "sort_order": 0,
          "children": []
        }
      ]
    }
  ]
}
```

#### 2.1.2 创建分类

- **URL**: `/api/courses/categories/`
- **Method**: `POST`

**请求参数**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `name` | string | 是 | 分类名称 |
| `parent` | int | 否 | 父分类ID (一级分类不传或传null) |
| `sort_order` | int | 否 | 排序值 (默认0) |
| `image` | string | 否 | 封面图片URL |
| `description` | string | 否 | 描述 |

#### 2.1.3 更新/删除分类

- **更新**: `PUT/PATCH /api/courses/categories/{id}/`
- **删除**: `DELETE /api/courses/categories/{id}/`

---

### 2.2 课程管理

**基础路径**: `/api/courses/admin/list/`

#### 2.2.1 获取课程列表

- **URL**: `/api/courses/admin/list/`
- **Method**: `GET`
- **Parameters**: `page`, `page_size`

#### 2.2.2 创建课程

- **URL**: `/api/courses/admin/list/`
- **Method**: `POST`

**请求参数**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `title` | string | 是 | 课程名称 |
| `category` | int | 是 | 分类ID |
| `cover` | string | 否 | 封面图片URL |
| `description` | string | 否 | 课程简介 |
| `instructor` | string | 是 | 讲师姓名 |
| `access_level` | int | 否 | 访问权限 (0:所有, 1:VIP1, 2:VIP2...) |
| `is_published` | bool | 否 | 是否发布 |
| `status` | string | 否 | 状态 (UPDATING:更新中, FINISHED:已完结) |

---

### 2.3 章节管理

**基础路径**: `/api/courses/chapters/`

#### 2.3.1 创建章节

- **URL**: `/api/courses/chapters/`
- **Method**: `POST`

**请求参数**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `course` | int | 是 | 所属课程ID |
| `title` | string | 是 | 章节名称 |
| `description` | string | 否 | 章节描述 |
| `sort_order` | int | 否 | 排序值 |

---

### 2.4 课时管理

**基础路径**: `/api/courses/lessons/`

#### 2.4.1 创建课时

- **URL**: `/api/courses/lessons/`
- **Method**: `POST`

**请求参数**

| 字段名 | 类型 | 必选 | 描述 |
| :--- | :--- | :--- | :--- |
| `chapter` | int | 是 | 所属章节ID |
| `title` | string | 是 | 课时标题 |
| `description` | string | 否 | 课时描述 |
| `video_file_id` | string | 是 | 腾讯云点播 FileID |
| `video_cover` | string | 否 | 视频封面URL |
| `sort_order` | int | 否 | 排序值 |

---

## 3. 客户端接口 (Client)

**权限要求**: 公开接口 (部分需要登录)

### 3.1 课程列表

- **URL**: `/api/courses/list/`
- **Method**: `GET`
- **Auth**: 无需认证
- **Parameters**:
    - `category_id`: int (可选，筛选分类)
    - `page`: int
    - `page_size`: int

**响应示例**

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "title": "Python入门",
        "cover": "http://...",
        "instructor": "张三",
        "access_level": 0,
        "status": "FINISHED",
        "category_name": "后端开发"
      }
    ],
    "count": 100
  }
}
```

### 3.2 课程详情

- **URL**: `/api/courses/{id}/detail/`
- **Method**: `GET`
- **Auth**: 无需认证 (但会根据登录状态返回不同信息)
- **Description**: 获取课程详细信息，包含章节和课时列表。

**响应示例**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Python入门",
    "chapters": [
      {
        "id": 10,
        "title": "第一章：基础",
        "lessons": [
          {
            "id": 101,
            "title": "环境搭建",
            "video_cover": "http://...",
            "can_play": true // 是否有权限播放 (仅作前端展示参考)
          }
        ]
      }
    ]
  }
}
```

### 3.3 课时播放鉴权

- **URL**: `/api/courses/lessons/{id}/auth/`
- **Method**: `GET`
- **Auth**: 需要认证 (Bearer Token)
- **Description**: 检查用户是否有权限播放该课时。如果通过，返回播放凭证（本期需求暂不需要播放凭证，仅做权限检查）。

**响应示例 (成功 - 允许播放)**

```json
{
  "success": true,
  "code": "OK",
  "data": {
    "allow": true,
    "file_id": "528589078..."
  }
}
```

**响应示例 (失败 - 权限不足)**

```json
{
  "success": false,
  "code": "PERMISSION_DENIED",
  "message": "需要Lv.1及以上会员"
}
```

**响应示例 (失败 - 会员过期)**

```json
{
  "success": false,
  "code": "AUTH_EXPIRED",
  "message": "会员已过期，请续费"
}
```
