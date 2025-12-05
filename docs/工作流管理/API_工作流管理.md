# 工作流管理 API 文档

## 1. 分类管理

### 1.1 获取分类列表
- **URL**: `/api/workflows/categories/`
- **Method**: `GET`
- **Permissions**: `IsAdminUser`
- **Response**:
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": [
    {
      "id": 1,
      "name": "分类名称",
      "cover": "url",
      "sort_order": 0,
      "description": "描述",
      "parent": null,
      "children": [
        {
          "id": 2,
          "name": "子分类",
          ...
        }
      ]
    }
  ]
}
```

### 1.2 创建分类
- **URL**: `/api/workflows/categories/`
- **Method**: `POST`
- **Permissions**: `IsAdminUser`
- **Body**:
```json
{
  "name": "分类名称",
  "cover": "url",
  "sort_order": 0,
  "description": "描述",
  "parent": null // 或父ID
}
```

### 1.3 更新分类
- **URL**: `/api/workflows/categories/{id}/`
- **Method**: `PUT`
- **Permissions**: `IsAdminUser`

### 1.4 删除分类
- **URL**: `/api/workflows/categories/{id}/`
- **Method**: `DELETE`
- **Permissions**: `IsAdminUser`

## 2. 工作流管理

### 2.1 获取工作流列表
- **URL**: `/api/workflows/list/`
- **Method**: `GET`
- **Permissions**: `IsAdminUser`
- **Params**:
  - `page`: 页码
  - `page_size`: 每页数量
  - `search`: 搜索关键词（标题、描述、标签）
  - `category`: 分类ID
  - `status`: 状态 (DRAFT/PUBLISHED)

### 2.2 创建工作流
- **URL**: `/api/workflows/list/`
- **Method**: `POST`
- **Permissions**: `IsAdminUser`
- **Body**:
```json
{
  "title": "工作流名称",
  "category": 1,
  "description": "描述",
  "start_node": "开始节点",
  "end_node": "结束节点",
  "node_details": "节点详情文本或JSON",
  "cover": "url",
  "video_url": "url",
  "attachment": "url",
  "reference": "参考资料",
  "tags": "tag1,tag2",
  "sort_order": 0,
  "status": "DRAFT", // PUBLISHED
  "access_level": 0 // 0: 免费, >0: 会员等级
}
```

### 2.3 更新工作流
- **URL**: `/api/workflows/list/{id}/`
- **Method**: `PUT`
- **Permissions**: `IsAdminUser`

### 2.4 删除工作流
- **URL**: `/api/workflows/list/{id}/`
- **Method**: `DELETE`
- **Permissions**: `IsAdminUser`
