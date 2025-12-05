from django.db import models
from apps.common.models import TimeStampedModel

class WorkflowCategory(TimeStampedModel):
    """工作流分类"""
    name = models.CharField(max_length=100, verbose_name="分类名称")
    cover = models.CharField(max_length=255, blank=True, null=True, verbose_name="封面")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        verbose_name="父级分类"
    )

    class Meta:
        verbose_name = "工作流分类"
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name


class Workflow(TimeStampedModel):
    """工作流"""
    STATUS_CHOICES = (
        ('DRAFT', '草稿'),
        ('PUBLISHED', '发布'),
    )

    title = models.CharField(max_length=200, verbose_name="工作流名称")
    category = models.ForeignKey(
        WorkflowCategory, 
        on_delete=models.CASCADE, 
        related_name='workflows', 
        verbose_name="分类"
    )
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    
    # 节点相关信息
    start_node = models.CharField(max_length=100, blank=True, null=True, verbose_name="开始节点")
    end_node = models.CharField(max_length=100, blank=True, null=True, verbose_name="结束节点")
    node_details = models.TextField(blank=True, null=True, verbose_name="节点详情") # JSON string or text description
    
    # 媒体与资源
    cover = models.CharField(max_length=255, blank=True, null=True, verbose_name="封面")
    video_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="演示视频")
    attachment = models.CharField(max_length=500, blank=True, null=True, verbose_name="附件")
    reference = models.TextField(blank=True, null=True, verbose_name="参考资料")
    
    tags = models.CharField(max_length=500, blank=True, null=True, verbose_name="标签") # 逗号分隔
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="状态")
    access_level = models.IntegerField(default=0, verbose_name="访问权限") # 0: 免费, >0: 会员等级

    class Meta:
        verbose_name = "工作流"
        verbose_name_plural = verbose_name
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title
