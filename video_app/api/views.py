from rest_framework import generics
from video_app.models import Video
from .serializers import VideoSerializer
from rest_framework.response import Response
from rest_framework import status

class VideoList(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

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