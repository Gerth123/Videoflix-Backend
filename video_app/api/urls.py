from django.urls import path
from .views import *


urlpatterns = [     
    path('', VideoList.as_view(), name='video-list'),
    path('videos/', VideoList.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoDetail.as_view(), name='video-detail'),
]