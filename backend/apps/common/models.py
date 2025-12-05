from django.db import models

class TimeStampedModel(models.Model):
    """
    抽象基类，提供创建时间和更新时间字段
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        abstract = True
