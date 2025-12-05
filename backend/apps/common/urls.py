from django.urls import path
from .views import FileUploadView, VodSignatureView

urlpatterns = [
    path('upload/file/', FileUploadView.as_view(), name='upload_file'),
    path('vod/signature/', VodSignatureView.as_view(), name='vod_signature'),
]
