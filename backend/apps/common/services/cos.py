import os
import uuid
import logging
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from django.conf import settings

logger = logging.getLogger('apps.common')

class CosService:
    def __init__(self):
        self.secret_id = os.environ.get("TENCENT_SECRET_ID")
        self.secret_key = os.environ.get("TENCENT_SECRET_KEY")
        self.region = os.environ.get("TENCENT_COS_REGION")
        self.bucket = os.environ.get("TENCENT_COS_BUCKET")
        self.scheme = 'https'
        
        if not all([self.secret_id, self.secret_key, self.region, self.bucket]):
            logger.error("COS configuration missing")
            raise ValueError("COS configuration missing")

        self.config = CosConfig(
            Region=self.region, 
            SecretId=self.secret_id, 
            SecretKey=self.secret_key, 
            Scheme=self.scheme
        )
        self.client = CosS3Client(self.config)

    def upload_file(self, file_obj, path_prefix="uploads"):
        """
        上传文件到 COS
        :param file_obj: 文件对象 (InMemoryUploadedFile)
        :param path_prefix: 路径前缀
        :return: 完整 URL
        """
        try:
            ext = file_obj.name.split('.')[-1] if '.' in file_obj.name else 'tmp'
            filename = f"{uuid.uuid4().hex}.{ext}"
            key = f"{path_prefix}/{filename}"
            
            response = self.client.upload_file_from_buffer(
                Bucket=self.bucket,
                Body=file_obj,
                Key=key
            )
            
            # 构建 URL
            url = f"{self.scheme}://{self.bucket}.cos.{self.region}.myqcloud.com/{key}"
            return url
        except Exception as e:
            logger.error(f"COS upload failed: {str(e)}")
            raise e
