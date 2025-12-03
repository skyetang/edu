from django.urls import path
from .views import (
    SendCodeView, RegisterView, LoginPasswordView, LoginCodeView, 
    UserProfileView, PasswordChangeView, VerifyPhoneView, ChangePhoneView,
    AvatarUploadView, RefreshTokenView
)


urlpatterns = [
    path('send_code', SendCodeView.as_view()),
    path('register', RegisterView.as_view()),
    path('login/password', LoginPasswordView.as_view()),
    path('login/code', LoginCodeView.as_view()),
    path('token/refresh', RefreshTokenView.as_view()),
    path('profile', UserProfileView.as_view()),
    path('profile/avatar', AvatarUploadView.as_view()),
    path('password/change', PasswordChangeView.as_view()),
    path('phone/verify-old', VerifyPhoneView.as_view()),
    path('phone/change-new', ChangePhoneView.as_view()),
]
