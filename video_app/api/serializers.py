from rest_framework import serializers
from video_app.models import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        request = kwargs.get('context', {}).get('request', None)
        if request and request.method == 'POST':
            self.fields = {
                'title': self.fields['title'],
                'description': self.fields['description'],
                'video_file': self.fields['video_file']
            }
        super().__init__(*args, **kwargs)

    def validate_video_file(self, value):
        if not value.name.endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("Nur Videodateien sind erlaubt.")
        return value
