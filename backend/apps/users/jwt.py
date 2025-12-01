import time
import jwt
from django.conf import settings


def issue_token(user_id: int, phone: str, expires_in: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "phone": phone, "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

