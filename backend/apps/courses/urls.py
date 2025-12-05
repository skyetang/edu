from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, CourseAdminViewSet, ChapterViewSet, LessonViewSet,
    CourseListView, CourseDetailView, LessonAuthView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'admin/list', CourseAdminViewSet, basename='admin-courses')
router.register(r'chapters', ChapterViewSet)
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    # Admin API (managed by router)
    path('', include(router.urls)),
    
    # Client API
    path('list/', CourseListView.as_view(), name='course-list'),
    path('<int:pk>/detail/', CourseDetailView.as_view(), name='course-detail'),
    path('lessons/<int:pk>/auth/', LessonAuthView.as_view(), name='lesson-auth'),
]
