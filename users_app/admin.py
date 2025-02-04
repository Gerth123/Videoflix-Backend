from django.contrib import admin
from .models import UserProfile
from video_app.models import Video

admin.site.register(UserProfile)
admin.site.register(Video)



