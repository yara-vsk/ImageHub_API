from django.contrib import admin
from django.urls import path, include
from image.views import ImageAPIView, get_expiring_link, ImageDownloadAPIView

urlpatterns = [
    path('api/v1/images/', ImageAPIView.as_view()),
    path('api/v1/create_expiring_link/', get_expiring_link),
    path('api/v1/download/', ImageDownloadAPIView.as_view()),
]