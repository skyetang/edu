from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CourseCategory, Course, CourseChapter, CourseLesson

User = get_user_model()

class CourseManagementTests(APITestCase):
    def setUp(self):
        # 创建管理员
        self.admin = User.objects.create_superuser(
            phone='13800138000',
            password='adminpassword'
        )
        # 创建普通用户
        self.user = User.objects.create_user(
            phone='13900139000',
            password='userpassword'
        )
        
        # 预设数据
        self.category = CourseCategory.objects.create(
            name="后端开发",
            sort_order=1
        )

    def test_create_category_admin(self):
        """测试管理员创建分类"""
        self.client.force_authenticate(user=self.admin)
        data = {
            "name": "Python进阶",
            "parent": self.category.id,
            "sort_order": 2
        }
        response = self.client.post('/api/courses/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Python进阶")
        self.assertEqual(response.data['parent'], self.category.id)

    def test_create_category_permission(self):
        """测试普通用户无法创建分类"""
        self.client.force_authenticate(user=self.user)
        data = {"name": "黑客教程"}
        response = self.client.post('/api/courses/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_course_admin(self):
        """测试管理员创建课程"""
        self.client.force_authenticate(user=self.admin)
        data = {
            "title": "Django实战",
            "category": self.category.id,
            "instructor": "贝塔",
            "access_level": 0,
            "is_published": False,
            "status": "UPDATING"
        }
        response = self.client.post('/api/courses/admin/list/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Django实战")
        
        # 验证数据库
        self.assertTrue(Course.objects.filter(title="Django实战").exists())

    def test_course_list_client(self):
        """测试客户端课程列表（仅显示已发布）"""
        # 创建两个课程
        Course.objects.create(
            title="已发布课程", category=self.category, instructor="A", 
            is_published=True, sort_order=1
        )
        Course.objects.create(
            title="未发布课程", category=self.category, instructor="B", 
            is_published=False, sort_order=2
        )

        response = self.client.get('/api/courses/list/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "已发布课程")

    def test_chapter_lesson_management(self):
        """测试章节与课时管理"""
        self.client.force_authenticate(user=self.admin)
        
        # 1. 创建课程
        course = Course.objects.create(
            title="全栈开发", category=self.category, instructor="C"
        )
        
        # 2. 添加章节
        chapter_data = {
            "course": course.id,
            "title": "第一章：基础",
            "sort_order": 1
        }
        res_chapter = self.client.post('/api/courses/chapters/', chapter_data)
        self.assertEqual(res_chapter.status_code, status.HTTP_201_CREATED)
        chapter_id = res_chapter.data['id']
        
        # 3. 添加课时
        lesson_data = {
            "course": course.id,
            "chapter": chapter_id,
            "title": "环境搭建",
            "video_file_id": "123456",
            "sort_order": 1
        }
        res_lesson = self.client.post('/api/courses/lessons/', lesson_data)
        self.assertEqual(res_lesson.status_code, status.HTTP_201_CREATED)
        
        # 4. 验证课程详情包含章节
        # 使用管理员权限获取详情（应能看到）
        # 注意：之前修改了 CourseDetailView 允许 AllowAny 但根据 is_published 过滤
        # 如果课程未发布，普通用户看不到，但管理员能看到
        
        # 测试未发布课程，普通用户看不到
        self.client.force_authenticate(user=self.user)
        res_detail = self.client.get(f'/api/courses/{course.id}/detail/')
        self.assertEqual(res_detail.status_code, status.HTTP_404_NOT_FOUND)
        
        # 测试未发布课程，管理员能看到
        self.client.force_authenticate(user=self.admin)
        res_detail_admin = self.client.get(f'/api/courses/{course.id}/detail/')
        self.assertEqual(res_detail_admin.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_detail_admin.data['data']['chapters']), 1)
        self.assertEqual(res_detail_admin.data['data']['chapters'][0]['lessons'][0]['title'], "环境搭建")
