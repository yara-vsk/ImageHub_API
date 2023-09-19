from django.contrib import admin
from django.urls import path, include
from image.views import ImageAPIView, get_signed_url, get_image_by_link

urlpatterns = [
    path('api/v1/images/', ImageAPIView.as_view()),
    path('api/v1/create_expiring_link/', get_signed_url),
    path('api/v1/download/', get_image_by_link),
]