import random
from django.core.cache import cache
from django.conf import settings
from .models import User


def _code_key(phone: str, scene: str) -> str:
    return f"sms:{scene}:{phone}"


def _rate_key(phone: str, scene: str) -> str:
    return f"smsrate:{scene}:{phone}"


def generate_code() -> str:
    return f"{random.randint(100000, 999999)}"


def send_code(phone: str, scene: str) -> bool:
    if cache.get(_rate_key(phone, scene)):
        return False
    code = generate_code()
    cache.set(_code_key(phone, scene), code, timeout=300)
    cache.set(_rate_key(phone, scene), 1, timeout=60)
    if settings.DEBUG:
        print(f"SMS {scene} {phone} {code}")
        return True
    try:
        from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dysmsapi20170525 import models as dysmsapi_models

        config = open_api_models.Config(
            access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
            access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
        )
        config.endpoint = "dysmsapi.aliyuncs.com"
        client = DysmsapiClient(config)
        request = dysmsapi_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=settings.ALIYUN_SMS_SIGN_NAME,
            template_code=settings.ALIYUN_SMS_TEMPLATE_CODE,
            template_param=f'{{"code":"{code}"}}',
        )
        client.send_sms(request)
        return True
    except Exception:
        return False


def verify_code(phone: str, scene: str, code: str) -> bool:
    saved = cache.get(_code_key(phone, scene))
    if not saved:
        return False
    if str(saved) != str(code):
        return False
    cache.delete(_code_key(phone, scene))
    return True

