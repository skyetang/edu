# 网站项目规则（Vue3 / Django + MySQL + Redis）

## 6A 工作流激活
- 输入以 `6A` 或 `@6A` 开头的任务描述即启动工作流；显示当前阶段与下一步。
- 六阶段：Align（对齐）→ Architect（架构）→ Atomize（原子化）→ Approve（审批）→ Automate（执行）→ Assess（评估）。

## Align（对齐）
- 交付：`docs/任务名/ALIGNMENT_任务名.md`（需求、边界、疑问清单、确认记录）。
- 质量门控：范围收敛、验收标准可测试、与现有架构一致。

## Architect（架构）
- 交付：`docs/任务名/DESIGN_任务名.md`（架构图、模块依赖、接口契约、数据流与异常策略）。
- 前端：目录 `src/components|views|router|store|services|composables|assets`；Axios 实例与拦截器统一；服务层仅返回数据或抛错。
- 后端：`settings/base|dev|prod.py` 拆分；`django-environ` 管理环境；统一响应封装与异常处理；MySQL 索引与约束评审；Redis 用于缓存与会话。

## Atomize（原子化）
- 交付：`docs/任务名/TASK_任务名.md`（输入/输出契约、实现约束、依赖关系、验收标准、mermaid 依赖图）。
- 原则：复杂度可控、独立可测、依赖清晰。

## Approve（审批）
- 检查：完整性、一致性、可行性、可测性、风险可控。
- 确认：实现需求明确、子任务清晰、边界与限制明确、验收标准明确、代码/测试/文档质量标准齐备。

## Automate（执行）
- 质量脚本：
  - 前端：`eslint+prettier`、`vitest+c8`；可选 `tsc --noEmit`。
  - 后端：`ruff check`、`black --check`、`isort --check-only`、`pytest --cov`。
- 提交流程：Conventional Commits；PR 必须通过 lint/test/coverage 阈值。

## Assess（评估）
- 验收：覆盖率≥80%（关键服务≥90%）、性能基准、依赖安全扫描。
- 交付：`docs/任务名/FINAL_任务名.md`、`docs/任务名/TODO_任务名.md`；包含回滚与数据迁移回退方案。

## 接口返回统一结构
```json
{
  "success": true,
  "code": "OK",
  "message": "ok",
  "data": {},
  "meta": {
    "pagination": { "page": 1, "page_size": 20, "total": 100 }
  },
  "request_id": "uuid-or-trace-id"
}
```
- 建议错误码 ↔ HTTP 状态：`OK→200`、`VALIDATION_ERROR→422`、`AUTH_EXPIRED→401`、`PERMISSION_DENIED→403`、`NOT_FOUND→404`、`CONFLICT→409`、`RATE_LIMITED→429`、`SERVER_ERROR→500`、`UNKNOWN_ERROR→520`。

## 后端统一异常处理（DRF）
```python
from rest_framework.response import Response
from rest_framework.views import exception_handler

def ok(data=None, message="ok", meta=None, request_id=None, status=200):
    return Response({
        "success": True,
        "code": "OK",
        "message": message,
        "data": data,
        "meta": meta,
        "request_id": request_id,
    }, status=status)

def error(code, message, data=None, meta=None, request_id=None, status=400):
    return Response({
        "success": False,
        "code": code,
        "message": message,
        "data": data,
        "meta": meta,
        "request_id": request_id,
    }, status=status)

def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get("request")
    request_id = getattr(request, "request_id", None)
    if response is not None:
        detail = None
        if isinstance(response.data, dict):
            detail = response.data.get("detail")
        message = detail or str(exc)
        code = "VALIDATION_ERROR" if response.status_code in (400, 422) else "SERVER_ERROR"
        response.data = {
            "success": False,
            "code": code,
            "message": message,
            "data": None,
            "meta": None,
            "request_id": request_id,
        }
    return response
```
- DRF 设置：
```python
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "config.settings.unified_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

## 前端统一处理（Axios 拦截器）
```ts
import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/store/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = useAuthStore().token
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && body.success) return body.data
    const code = body?.code || 'UNKNOWN_ERROR'
    const message = body?.message || '请求失败'
    handleBusinessError(code, message, body)
    return Promise.reject({ code, message, body })
  },
  (error) => {
    const status = error.response?.status
    const message = error.message || '网络错误'
    handleHttpError(status, message, error)
    return Promise.reject(error)
  }
)

function handleBusinessError(code: string, message: string, body: any) {
  switch (code) {
    case 'AUTH_EXPIRED':
      useAuthStore().logout()
      router.push('/login')
      break
    case 'PERMISSION_DENIED':
      router.push('/403')
      break
    case 'NOT_FOUND':
      router.push('/404')
      break
    case 'VALIDATION_ERROR':
      break
    case 'RATE_LIMITED':
      break
    default:
      break
  }
}

function handleHttpError(status?: number, message?: string, error?: any) {
  switch (status) {
    case 401:
      useAuthStore().logout()
      router.push('/login')
      break
    case 403:
      router.push('/403')
      break
    case 404:
      router.push('/404')
      break
    case 429:
      break
    default:
      break
  }
}

export default api
```

## 错误与消息提示规范
- 分类：用户可行动错误（校验、权限、认证）、系统错误（网络、服务器）、信息与成功提示（轻量、不打断）。
- 文案：短句、动作导向、支持 i18n；敏感信息不暴露；避免技术细节外泄。
- 防抖与去重：同一错误短时间只提示一次；聚合重复消息。
- 展示：字段就地错误；路由级 403/404；登录重定向；速率限制提示与重试入口。

## 前端样式与响应式规范
- 设计系统：统一色板、间距、阴影、圆角与排版；组件库可选（如 Element Plus 或自研）。
- 样式方案：TailwindCSS 或 SCSS 模块化；禁止内联样式；变量集中于主题文件。
- 响应式断点建议：`sm 640px`、`md 768px`、`lg 1024px`、`xl 1280px`、`2xl 1536px`；移动优先。
- 组件规范：展示组件不发请求；容器组件负责数据与状态；表单就地校验与摘要错误。
- 可访问性：语义标签、可聚焦、键盘可用、对比度达标。

## 测试与质量门槛
- 前端：`vitest` + `@vue/test-utils`；关键流程端到端（`playwright`/`cypress`）；覆盖率目标 ≥ 80%。
- 后端：`pytest` + `pytest-django`；关键服务层 ≥ 90% 行覆盖率。
- 静态检查：前端 `eslint+prettier`；后端 `ruff+black+isort`；预提交统一执行。

## 环境与安全
- 环境变量示例：
```env
DJANGO_SECRET_KEY=changeme
DJANGO_DEBUG=false
DATABASE_URL=mysql://user:pass@host:3306/dbname
REDIS_URL=redis://host:6379/0
ALLOWED_HOSTS=your.domain
CORS_ALLOWED_ORIGINS=https://frontend.domain
VITE_API_BASE_URL=https://api.domain
```
- 禁止提交真实 `.env`；生产开启 TLS、HSTS、Secure Cookies；CORS 最小化放行。

## CI/CD 与协作
- 分支：`main`、`develop`、`feature/*`、`fix/*`、`release/*`；PR 准入：lint/test/coverage 达标。
- 预提交钩子：后端 `ruff, black, isort, pytest`；前端 `eslint, prettier`；`commit-msg` 检查 Conventional Commits。
- 部署：前端 `vite build` + CDN；后端容器化 `gunicorn/uvicorn` + NGINX + TLS；发布前执行 `migrate`；监控慢查询与缓存命中率。
