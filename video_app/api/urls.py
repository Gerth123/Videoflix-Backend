from django.urls import path
from .views import VideoList, VideoDetail, VideoThumbnail, GenreGroupedVideosView, BigThumbnailView


urlpatterns = [
    path('', VideoList.as_view(), name='video-list'),
    path('videos/', VideoList.as_view(), name='video-list'),
    path('videos/<int:pk>/', VideoDetail.as_view(), name='video-detail'),
    path('videos/<int:pk>/thumbnail/', VideoThumbnail.as_view(), name='video-thumbnail'),
    path('genres/', GenreGroupedVideosView.as_view(), name='genres-grouped'),
    path('big-thumbnail/', BigThumbnailView.as_view(), name='big-thumbnail'),
]
