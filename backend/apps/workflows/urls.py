from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowCategoryViewSet, WorkflowViewSet

router = DefaultRouter()
router.register(r'categories', WorkflowCategoryViewSet)
router.register(r'list', WorkflowViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
