from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from .models import CourseCategory, Course, CourseChapter, CourseLesson
from apps.membership.models import MembershipPlan

class CourseCategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, required=False)

    class Meta:
        model = CourseCategory
        fields = '__all__'
        extra_kwargs = {
            'parent': {'required': False}
        }
    
    def to_internal_value(self, data):
        # 如果前端传回了 RecursiveField 的数据，在写入时忽略它
        if 'children' in data:
            data = data.copy()
            data.pop('children')
        return super().to_internal_value(data)

class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    access_level_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
    
    def get_access_level_name(self, obj):
        if obj.access_level == 0:
            return "免费"
        try:
            plan = MembershipPlan.objects.filter(level=obj.access_level).first()
            return plan.name if plan else f"VIP Lv.{obj.access_level}"
        except Exception:
            return f"VIP Lv.{obj.access_level}"

class CourseLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLesson
        fields = '__all__'

class CourseChapterSerializer(serializers.ModelSerializer):
    lessons = CourseLessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = CourseChapter
        fields = '__all__'

class CourseDetailSerializer(CourseSerializer):
    chapters = CourseChapterSerializer(many=True, read_only=True)
