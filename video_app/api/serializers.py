from rest_framework import serializers
from video_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'thumbnail', 'video_144p',
                            'video_240p', 'video_360p', 'video_480p', 'video_720p', 'video_1080p']

    def __init__(self, *args, **kwargs):
        """
        Initializes the VideoSerializer instance and customizes the fields based on the request method.

        If the request method is 'POST', only the 'title', 'description', and 'video_file' fields
        are retained in the serializer. Other fields are removed to restrict the input fields
        available during video creation.

        :param args: Additional positional arguments passed to the parent's __init__ method.
        :param kwargs: Additional keyword arguments passed to the parent's __init__ method.
        """
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request and request.method == 'POST':
            allowed = ['title', 'description', 'video_file']
            existing = list(self.fields.keys())
            for field_name in existing:
                if field_name not in allowed:
                    self.fields.pop(field_name)

    def validate_video_file(self, value):
        """
        Validates the video_file field.

        :param value: The video file to be validated.
        :return: The validated video file.
        :raises serializers.ValidationError: If the video file name is not valid.
        """
        if not value.name.endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("Nur Videodateien sind erlaubt.")
        return value


class VideoThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['thumbnail', 'title']


class VideoBigThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['thumbnail', 'title', 'description']
