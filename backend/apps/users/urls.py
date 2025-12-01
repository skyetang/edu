from django.urls import path
from .views import SendCodeView, RegisterView, LoginPasswordView, LoginCodeView


urlpatterns = [
    path('send_code', SendCodeView.as_view()),
    path('register', RegisterView.as_view()),
    path('login/password', LoginPasswordView.as_view()),
    path('login/code', LoginCodeView.as_view()),
]

