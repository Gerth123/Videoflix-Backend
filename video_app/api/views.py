from rest_framework import generics
from video_app.models import Video
from .serializers import VideoSerializer, VideoThumbnailSerializer, VideoBigThumbnailSerializer
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
        """
        If a resolution is provided in the query parameters, return the video URL for this
        resolution. If the video does not exist in the given resolution, return a 404 status code.
        If the resolution is invalid, return a 400 status code. If no resolution is provided, return
        the video object as JSON, serialized by the VideoSerializer.
        """
        video = self.get_object()
        resolution = request.GET.get('resolution', None)
        if resolution:
            video_field = f"video_{resolution}"
            if hasattr(video, video_field):
                video_url = getattr(video, video_field).url if getattr(video, video_field) else None
                if video_url:
                    return Response({"video_url": video_url}, status=status.HTTP_200_OK)
                return Response({"error": "Video in dieser Auflösung nicht verfügbar."},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Ungültige Auflösung."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(video)
        return Response(serializer.data)


class VideoThumbnail(APIView):
    def get(self, request, pk, *args, **kwargs):
        """
        Returns the thumbnail URL for a given video id.

        If the video does not exist, a 404 status code is returned with the error message "Video nicht gefunden.".
        If the video does not have a thumbnail associated with it, a 404 status code is returned with the error message "Thumbnail nicht verfügbar.".
        If the thumbnail is successfully retrieved, a 200 status code is returned with the thumbnail URL as JSON data.
        """
        try:
            video = Video.objects.get(pk=pk)
            if video.thumbnail:
                return Response({
                    "thumbnail_url": video.thumbnail.url
                }, status=status.HTTP_200_OK)
            return Response({"error": "Thumbnail nicht verfügbar."}, status=status.HTTP_404_NOT_FOUND)

        except Video.DoesNotExist:
            return Response({"error": "Video nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)


class GenreGroupedVideosView(APIView):
    def get(self, request):
        """
        Returns a list of objects containing the genre name and a list of up to 6 movies in that genre.
        The first object in the list is a special 'New on Videoflix' group, which contains the latest 6 movies.
        The rest of the objects are grouped by genre, and contain up to 6 movies in that genre.
        """
        genres = Video.objects.values_list('genre', flat=True).distinct()
        result = []
        latest_videos = Video.objects.order_by('-created_at')[:6]
        serialized_latest = VideoThumbnailSerializer(latest_videos, many=True)
        result.append({
            'name': 'New on Videoflix',
            'movies': [{'thumbnailUrl': vid['thumbnail'], 'title': vid['title']} for vid in serialized_latest.data]
        })
        for genre in genres:
            videos = Video.objects.filter(genre=genre).order_by('-created_at')
            serialized = VideoThumbnailSerializer(videos, many=True)
            result.append({
                'name': genre.title(),
                'movies': [{'thumbnailUrl': vid['thumbnail'], 'title': vid['title']} for vid in serialized.data]
            })
        return Response(result)


class BigThumbnailView(APIView):
    def get(self, request):
        """
        Returns the latest video's big thumbnail and title.

        Returns a JSON object with 'thumbnailUrl' and 'title' keys.

        If no videos are available, returns a 404 response with a message.
        """
        latest_video = Video.objects.order_by('-created_at').first()

        if latest_video:
            serialized_video = VideoBigThumbnailSerializer(latest_video)
            return Response(serialized_video.data)
        else:
            return Response({'message': 'No videos available'}, status=404)
