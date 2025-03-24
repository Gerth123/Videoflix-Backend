from django.conf import settings
from rest_framework import generics
from video_app.models import Video
from .serializers import VideoSerializer


class VideoList(generics.ListCreateAPIView):
    pass


class VideoDetail(generics.RetrieveUpdateDestroyAPIView):
    pass