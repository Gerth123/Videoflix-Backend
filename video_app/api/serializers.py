from rest_framework import serializers
from video_app.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'thumbnail', 'video_144p',
                            'video_240p', 'video_360p', 'video_480p', 'video_720p', 'video_1080p']
    
    # def __init__(self, *args, **kwargs):
    #     request = kwargs.get('context', {}).get('request', None)
    #     if request and request.method == 'POST':
    #         self.fields = {
    #             'title': self.fields['title'],
    #             'description': self.fields['description'],
    #             'video_file': self.fields['video_file']
    #         }
    #     super().__init__(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request and request.method == 'POST':
            allowed = ['title', 'description', 'video_file']
            existing = list(self.fields.keys())
            for field_name in existing:
                if field_name not in allowed:
                    self.fields.pop(field_name)


    def validate_video_file(self, value):
        if not value.name.endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("Nur Videodateien sind erlaubt.")
        return value
