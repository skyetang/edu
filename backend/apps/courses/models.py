from django.db import models

class CourseCategory(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="父级分类")
    name = models.CharField(max_length=50, verbose_name="分类名称")
    cover = models.CharField(max_length=255, blank=True, verbose_name="封面图URL", help_text="COS URL")
    description = models.TextField(blank=True, verbose_name="描述")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "course_categories"
        ordering = ['sort_order', 'id']
        verbose_name = "课程分类"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Course(models.Model):
    STATUS_CHOICES = (
        ('UPDATING', '更新中'),
        ('FINISHED', '已完结'),
    )
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses', verbose_name="所属分类")
    title = models.CharField(max_length=100, verbose_name="课程名称")
    cover = models.CharField(max_length=255, blank=True, verbose_name="封面图URL")
    description = models.TextField(blank=True, verbose_name="课程描述")
    instructor = models.CharField(max_length=50, verbose_name="讲师姓名", help_text="讲师姓名")
    access_level = models.IntegerField(default=0, verbose_name="访问权限", help_text="0:免费, >0:所需会员等级")
    is_published = models.BooleanField(default=False, verbose_name="是否发布")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPDATING', verbose_name="状态")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        ordering = ['sort_order', '-created_at']
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

class CourseChapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name="所属课程")
    title = models.CharField(max_length=100, verbose_name="章节名称")
    description = models.TextField(blank=True, verbose_name="章节描述")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_chapters"
        ordering = ['sort_order', 'id']
        verbose_name = "课程章节"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class CourseLesson(models.Model):
    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='lessons', verbose_name="所属章节")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="所属课程") # 冗余字段方便查询
    title = models.CharField(max_length=100, verbose_name="课时标题")
    description = models.TextField(blank=True, verbose_name="课时描述")
    cover = models.CharField(max_length=255, blank=True, verbose_name="视频封面", help_text="VOD cover url")
    video_file_id = models.CharField(max_length=100, verbose_name="视频FileId", help_text="腾讯云VOD FileId")
    video_url = models.CharField(max_length=500, blank=True, verbose_name="视频播放地址", help_text="VOD video url")
    duration = models.CharField(max_length=20, blank=True, verbose_name="时长", help_text="e.g. 08:50")
    resolution = models.CharField(max_length=20, blank=True, verbose_name="分辨率", help_text="e.g. 1920x1080")
    sort_order = models.IntegerField(default=0, verbose_name="排序值")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_lessons"
        ordering = ['sort_order', 'id']
        verbose_name = "课时"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
