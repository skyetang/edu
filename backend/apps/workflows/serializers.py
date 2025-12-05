from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from .models import WorkflowCategory, Workflow
from apps.membership.models import MembershipPlan

class WorkflowCategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, required=False)

    class Meta:
        model = WorkflowCategory
        fields = '__all__'
        extra_kwargs = {
            'parent': {'required': False}
        }

    def validate(self, attrs):
        # 限制层级：只允许一级子类
        parent = attrs.get('parent')
        if parent and parent.parent:
            raise serializers.ValidationError("最多只支持两级分类")
        return attrs
        
    def to_internal_value(self, data):
        if 'children' in data:
            data = data.copy()
            data.pop('children')
        return super().to_internal_value(data)


class WorkflowSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    access_level_name = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = '__all__'

    def get_access_level_name(self, obj):
        if obj.access_level == 0:
            return "免费"
        try:
            plan = MembershipPlan.objects.filter(level=obj.access_level).first()
            return plan.name if plan else f"VIP Lv.{obj.access_level}"
        except Exception:
            return f"VIP Lv.{obj.access_level}"
