# 会员与订单模块接口文档

本文档描述了会员套餐管理、订单创建、支付及订单状态流转相关的 API 接口。

## 1. 基础信息

- **Base URL**: `/api/membership`
- **Auth**: 大部分接口需要 Bearer Token 认证
- **Response**: 遵循统一响应结构 (参考 Auth 文档)

---

## 2. 接口详情

### 2.1 获取/管理套餐列表

- **URL**: `/api/membership/plans/`
- **Method**: `GET`, `POST`, `PATCH`, `DELETE`
- **Auth**: 
  - `GET`: 登录用户或游客均可（游客/普通用户仅见启用套餐，管理员见所有）
  - `POST/PATCH/DELETE`: 仅限管理员 (`is_staff=True`)

#### 2.1.1 获取套餐列表 (GET)

**Query Params**: 无

**响应示例**:
```json
{
  "success": true,
  "code": "OK",
  "data": [
    {
      "id": 1,
      "name": "月度会员",
      "price": "29.90",
      "original_price": "39.90",
      "duration_days": 30,
      "level": 1,
      "is_active": true,
      "description": "特权1\n特权2"
    }
  ]
}
```

#### 2.1.2 创建套餐 (POST - Admin)

**请求参数**:
```json
{
  "name": "季度会员",
  "price": 88.00,
  "duration_days": 90,
  "level": 1,
  "description": "..."
}
```

#### 2.1.3 删除套餐 (DELETE - Admin)

**Query Param**: `id` (套餐ID)

**说明**: 
- 若套餐无关联历史订单，将执行物理删除。
- **若套餐有关联订单，将执行软删除（仅设置 `is_active=False`），并返回提示信息。**

---

### 2.2 创建会员订单

- **URL**: `/api/membership/orders/create/`
- **Method**: `POST`
- **Auth**: 需认证

**功能**: 创建新订单（新购、续费或升级）。
**逻辑**:
1. 检查是否存在未支付的有效订单（PENDING 且未过期）。若存在，拒绝创建。
2. 自动判断订单类型 (`NEW`, `RENEWAL`, `UPGRADE`) 并计算金额（含升级折算）。
3. 使用数据库锁防止并发重复下单。

**请求参数**:
```json
{
  "plan_id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "order_no": "VIP20231027...",
    "amount": "29.90",
    "status": "PENDING",
    "remaining_seconds": 1800
  }
}
```

---

### 2.3 获取订单详情

- **URL**: `/api/membership/orders/detail/`
- **Method**: `GET`
- **Auth**: 需认证 (用户仅能看自己，管理员可看所有)

**Query Param**: `order_no`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "order_no": "...",
    "status": "PENDING",
    "plan_name": "月度会员",
    "amount": "29.90",
    "created_at": "...",
    "remaining_seconds": 1750 // 剩余支付秒数
  }
}
```

---

### 2.4 支付订单

- **URL**: `/api/membership/orders/pay/`
- **Method**: `POST`
- **Auth**: 需认证 (仅限本人支付)

**说明**: 模拟支付接口。支付成功后自动更新用户会员权益。

**请求参数**:
```json
{
  "order_no": "...",
  "payment_method": "ALIPAY" // ALIPAY, WECHAT
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "支付成功，会员已开通"
}
```

---

### 2.5 获取订单列表

- **URL**: `/api/membership/orders/list/`
- **Method**: `GET`
- **Auth**: 需认证

**Query Param**: 
- `scope`: 可选。管理员传 `my` 可只看自己订单；默认管理员看所有，普通用户看自己。

**响应示例**:
```json
{
  "success": true,
  "data": [ ... ] // 订单列表数组
}
```

---

### 2.6 订单操作（取消/退款）

- **URL**: `/api/membership/orders/action/`
- **Method**: `POST`
- **Auth**: 需认证

**请求参数**:
```json
{
  "order_no": "...",
  "action": "cancel" // 或 "refund"
}
```

**动作说明**:
- `cancel`: 取消未支付订单。用户可取消自己，管理员可取消任意。
- `refund`: **仅管理员可用**。退款已支付订单，并回滚扣除对应的会员时长与权益。
