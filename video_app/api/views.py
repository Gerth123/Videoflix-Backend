from rest_framework import generics
from video_app.models import Video
from .serializers import VideoSerializer, VideoThumbnailSerializer
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsAdminOrReadOnly
from rest_framework.views import APIView    

class VideoList(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAdminOrReadOnly]


class VideoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get(self, request, *args, **kwargs):
        video = self.get_object()
        resolution = request.GET.get('resolution', None)
        
        if resolution:
            video_field = f"video_{resolution}"
            if hasattr(video, video_field):
                video_url = getattr(video, video_field).url if getattr(video, video_field) else None
                if video_url:
                    return Response({"video_url": video_url}, status=status.HTTP_200_OK)
                return Response({"error": "Video in dieser Auflösung nicht verfügbar."}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Ungültige Auflösung."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(video)
        return Response(serializer.data)
    
class VideoThumbnail(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            video = Video.objects.get(pk=pk)

            # Gebe nur das Thumbnail zurück, wenn es vorhanden ist
            if video.thumbnail:
                return Response({
                    "thumbnail_url": video.thumbnail.url
                }, status=status.HTTP_200_OK)
            return Response({"error": "Thumbnail nicht verfügbar."}, status=status.HTTP_404_NOT_FOUND)

        except Video.DoesNotExist:
            return Response({"error": "Video nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
class GenreGroupedVideosView(APIView):
    def get(self, request):
        genres = Video.objects.values_list('genre', flat=True).distinct()
        result = []

        latest_videos = Video.objects.order_by('-created_at')[:6]
        serialized_latest = VideoThumbnailSerializer(latest_videos, many=True)
        result.append({
            'name': 'New on Videoflix',
            'movies': [{'thumbnailUrl': vid['thumbnail']} for vid in serialized_latest.data]
        })

        for genre in genres:
            videos = Video.objects.filter(genre=genre).order_by('-created_at')
            serialized = VideoThumbnailSerializer(videos, many=True)
            result.append({
                'name': genre.title(),
                'movies': [{'thumbnailUrl': vid['thumbnail']} for vid in serialized.data]
            })

        return Response(result)
