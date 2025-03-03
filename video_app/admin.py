from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Video


class VideoResource(resources.ModelResource):
    class Meta:
        model = Video

@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    resource_class = VideoResource

    def get_fields(self, request, obj=None):
        if obj: 
            return [field.name for field in self.model._meta.fields]
        return ["title", "description", "video_file"] 

    def get_readonly_fields(self, request, obj=None):
        if obj: 
            return ["video_144p", "video_240p", "video_360p", "video_480p", "video_720p", "video_1080p"]
        return []

