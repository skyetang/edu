import os
import time
import random
import base64
import hmac
import hashlib
import logging
import string
import jwt
from django.conf import settings

logger = logging.getLogger('apps.common')

class VodService:
    def __init__(self):
        self.secret_id = os.environ.get("TENCENT_SECRET_ID")
        self.secret_key = os.environ.get("TENCENT_SECRET_KEY")
        self.sub_app_id = os.environ.get("TENCENT_VOD_SUB_APP_ID") or os.environ.get("TENCENT_VOD_APP_ID")
        self.play_key = os.environ.get("TENCENT_PLAY_KEY") # Needed for play signature
        self.license_url = os.environ.get("TENCENT_LICENSE_URL", "")
        
        # Optional configs with defaults
        self.procedure = os.environ.get("TENCENT_PROCEDURE", "")
        self.storage_region = os.environ.get("TENCENT_STORAGE_REGION", "")
        self.class_id = os.environ.get("TENCENT_CLASS_ID", "")
        
        # Play config defaults
        self.rlimit = int(os.environ.get("TENCENT_RLIMIT", "3"))
        self.audio_video_type = os.environ.get("TENCENT_AUDIO_VIDEO_TYPE", "Original")
        # private_encryption_definition should be int if present
        self.private_encryption_definition = os.environ.get("TENCENT_PRIVATE_ENCRYPTION_DEFINITION") 

        if not all([self.secret_id, self.secret_key, self.sub_app_id]):
            logger.error("VOD configuration missing")
            raise ValueError("VOD configuration missing")

    def get_upload_signature(self):
        """
        生成 VOD 上传签名 (Client Upload Signature)
        参考: https://cloud.tencent.com/document/product/266/9221
        """
        current_time = int(time.time())
        expire_time = current_time + 3600  # 1小时有效期
        random_num = random.randint(0, 999999)
        
        # 构造原始签名字符串
        original_parts = [
            f"secretId={self.secret_id}",
            f"currentTimeStamp={current_time}",
            f"expireTime={expire_time}",
            f"random={random_num}",
        ]

        # 添加可选参数
        if self.procedure:
            original_parts.append(f"procedure={self.procedure}")
        
        if self.sub_app_id:
             original_parts.append(f"vodSubAppId={self.sub_app_id}")
             
        if self.storage_region:
            original_parts.append(f"storageRegion={self.storage_region}")
            
        if self.class_id:
            original_parts.append(f"classId={self.class_id}")

        original = "&".join(original_parts)
        
        # HMAC-SHA1 加密
        hmac_obj = hmac.new(
            bytes(self.secret_key, 'utf-8'),
            bytes(original, 'utf-8'),
            hashlib.sha1
        )
        sha1_digest = hmac_obj.digest()
        
        # 拼接并 Base64 编码
        signature_bytes = sha1_digest + bytes(original, 'utf-8')
        signature = base64.b64encode(signature_bytes).decode('utf-8')
        
        return signature

    def generate_random_str(self, length=10):
        characters = string.ascii_lowercase + string.digits
        return ''.join(random.choices(characters, k=length))

    def get_play_signature(self, file_id):
        """
        生成视频播放签名 (Video Play Signature)
        """
        if not file_id:
            raise ValueError("file_id is required")
            
        if not self.play_key:
             logger.error("TENCENT_PLAY_KEY missing")
             raise ValueError("TENCENT_PLAY_KEY missing")

        current_time = int(time.time())
        psign_expire = current_time + 7200  # 2小时有效期
        url_time_expire = hex(psign_expire)[2:]
        random_str = self.generate_random_str()

        content_info = {
            "audioVideoType": self.audio_video_type
        }

        if self.private_encryption_definition:
            try:
                content_info["drmAdaptiveInfo"] = {
                    "privateEncryptionDefinition": int(self.private_encryption_definition)
                }
            except ValueError:
                logger.warning(f"Invalid TENCENT_PRIVATE_ENCRYPTION_DEFINITION: {self.private_encryption_definition}")

        # Adjust payload structure according to documentation
        payload = {
            "appId": int(self.sub_app_id), # Must be Integer
            "fileId": file_id,
            "currentTimeStamp": current_time,
            "expireTimeStamp": psign_expire,
            "urlAccessInfo": {
                "t": url_time_expire,
                "us": random_str,
                "rlimit": self.rlimit
            },
            "contentInfo": content_info
        }

        print(f"DEBUG VOD Payload: {payload}")

        signature = jwt.encode(
            payload,
            self.play_key,
            algorithm='HS256'
        )

        return {
            "signature": signature,
            "psign_expire": psign_expire,
            "app_id": self.sub_app_id,
            "license_url": self.license_url
        }
