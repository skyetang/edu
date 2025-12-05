import time
import random
import base64
import hmac
import hashlib
import logging
import os
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from config.response import ok, error
from apps.common.services.vod import VodService
from apps.common.views import UnifiedModelViewSet
from .models import CourseCategory, Course, CourseChapter, CourseLesson
from .serializers import (
    CourseCategorySerializer, CourseSerializer, CourseDetailSerializer,
    CourseChapterSerializer, CourseLessonSerializer
)

# --- 管理端接口 ---

class CategoryViewSet(UnifiedModelViewSet):
    queryset = CourseCategory.objects.all()
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        # 仅返回一级分类，子分类通过 RecursiveField 嵌套返回
        queryset = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return ok(serializer.data)

class CourseAdminViewSet(UnifiedModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_published']
    search_fields = ['title', 'instructor']
    ordering_fields = ['sort_order', 'created_at']

class ChapterViewSet(UnifiedModelViewSet):
    queryset = CourseChapter.objects.all()
    serializer_class = CourseChapterSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']
    pagination_class = None

class LessonViewSet(UnifiedModelViewSet):
    queryset = CourseLesson.objects.all()
    serializer_class = CourseLessonSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['chapter', 'course']
    pagination_class = None

# --- 客户端接口 ---

class CourseListView(ListAPIView):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'instructor']
    ordering_fields = ['sort_order', 'created_at']

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return ok(response.data)

class CourseDetailView(RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Course.objects.all()
        return Course.objects.filter(is_published=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ok(serializer.data)

class LessonAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            lesson = CourseLesson.objects.get(pk=pk)
            course = lesson.course
            user = request.user

            # 权限检查
            if course.access_level > 0:
                # 1. 检查会员是否过期
                if not user.membership_expire_at or user.membership_expire_at < timezone.now():
                    return error("AUTH_EXPIRED", "会员已过期，请续费", status=403)
                
                # 2. 检查会员等级
                if user.level < course.access_level:
                    return error("PERMISSION_DENIED", f"需要Lv.{course.access_level}及以上会员", status=403)

            # 生成播放签名 (Key 防盗链)
            # 注意：此处仅为示例，实际需根据腾讯云 Key 防盗链规则生成
            # 通常需要: 路径(dir), 密钥(key), 过期时间(t), 试看(us)等
            # 假设简单返回 fileId 和 允许播放
            
            # 如果需要后端生成播放签名(假设开启了Key防盗链)
            # 参考: https://cloud.tencent.com/document/product/266/14047
            # 这里暂时只返回 fileId，前端直接使用 FileID 播放 (需配置 Referer 白名单)
            
            return ok({
                "allow": True,
                "file_id": lesson.video_file_id,
                "app_id": os.environ.get("TENCENT_VOD_APP_ID"),
                # "psign": "...", 
            })

        except CourseLesson.DoesNotExist:
            return error("NOT_FOUND", "课时不存在", status=404)
