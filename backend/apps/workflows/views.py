from rest_framework.permissions import IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from apps.common.views import UnifiedModelViewSet
from config.response import ok
from .models import WorkflowCategory, Workflow
from .serializers import WorkflowCategorySerializer, WorkflowSerializer

class WorkflowCategoryViewSet(UnifiedModelViewSet):
    queryset = WorkflowCategory.objects.all()
    serializer_class = WorkflowCategorySerializer
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request, *args, **kwargs):
        # 仅返回一级分类，子分类通过 RecursiveField 嵌套返回
        queryset = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return ok(serializer.data)

class WorkflowViewSet(UnifiedModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['sort_order', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
