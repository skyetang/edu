# 课程管理与公共服务模块设计 (Architect) v2

## 1. 模块依赖与技术栈
- **apps.common**:
  - 依赖: `cos-python-sdk-v5` (COS), `tencentcloud-sdk-python` (VOD Signature).
  - 职责: 统一处理文件上传(COS)与视频签名(VOD).
- **apps.courses**:
  - 依赖: `apps.users` (讲师/权限), `apps.common` (无直接代码依赖，但业务依赖其上传服务).
  - 职责: 课程体系 CRUD.

## 2. 数据库模型设计 (Detailed)

### 2.1 CourseCategory (课程分类)
```python
class CourseCategory(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=50)
    cover = models.CharField(max_length=255, blank=True, help_text="COS URL")
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['sort_order', 'id']
```

### 2.2 Course (课程)
```python
class Course(models.Model):
    STATUS_CHOICES = (
        ('UPDATING', '更新中'),
        ('FINISHED', '已完结'),
    )
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=100)
    cover = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    instructor = models.CharField(max_length=50, help_text="讲师姓名")
    access_level = models.IntegerField(default=0, help_text="0:免费, >0:所需会员等级")
    is_published = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPDATING')
    sort_order = models.IntegerField(default=0)
```

### 2.3 CourseChapter (章节)
```python
class CourseChapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
```

### 2.4 CourseLesson (课时)
```python
class CourseLesson(models.Model):
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='lessons')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons') # 冗余字段方便查询
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video_cover = models.CharField(max_length=255, blank=True)
    video_file_id = models.CharField(max_length=100, help_text="腾讯云VOD FileId")
    sort_order = models.IntegerField(default=0)
```

## 3. 核心服务实现逻辑

### 3.1 COS 服务 (apps/common/services/cos.py)
- 使用 `qcloud_cos.CosS3Client`.
- 方法 `upload_file(file_obj, path)`:
  - 生成唯一文件名 (UUID).
  - 调用 `client.upload_file_from_buffer`.
  - 拼接并返回完整 URL.

### 3.2 VOD 签名服务 (apps/common/services/vod.py)
- 使用手动构建签名字符串 (HMAC-SHA1) 或 `tencentcloud-sdk-python` 工具类.
- 关键参数: `procedure` (Upload), `expire_time`.
- 返回 Base64 编码的签名.

## 4. API 视图逻辑

### 4.1 图片上传接口
- 接收 `request.FILES['file']`.
- 校验文件类型 (image/*) 和大小.
- 调用 `CosService.upload_file`.
- 返回 `{"url": "..."}`.

### 4.2 播放鉴权接口 (apps/courses/views.py)
- 接收 `lesson_id`.
- 获取 `lesson.course.access_level`.
- 校验:
  - If `access_level == 0`: Pass.
  - If `user.level >= access_level` AND `!user.is_membership_expired()`: Pass.
  - Else: 403 Forbidden.
- 获取播放签名 (可选) 或直接返回 `fileId` 供前端播放器使用 (若配置了 Referer 防盗链，通常前端 SDK 需要 appId 和 fileId 即可; 若开启了 Key 防盗链，则需后端生成签名).
- **本次实现**: 假设开启 Key 防盗链，后端生成播放签名 `psign`.
