from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class CommonServiceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            phone='13800138000',
            password='userpassword'
        )

    @patch('apps.common.views.VodService')
    def test_vod_signature(self, mock_vod_service):
        """测试 VOD 签名生成"""
        # Mock return value
        mock_instance = mock_vod_service.return_value
        mock_instance.get_upload_signature.return_value = "mock_signature"

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/common/vod/signature/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['signature'], "mock_signature")

    @patch('apps.common.views.CosService')
    def test_image_upload(self, mock_cos_service):
        """测试图片上传"""
        mock_instance = mock_cos_service.return_value
        mock_instance.upload_file.return_value = "http://mock-cos-url.com/image.jpg"

        self.client.force_authenticate(user=self.user)
        
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post('/api/common/upload/image/', {'file': image}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['url'], "http://mock-cos-url.com/image.jpg")
