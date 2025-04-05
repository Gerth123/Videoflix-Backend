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
        fields = [field.name for field in self.opts.model._meta.fields]
        if obj:
            fields.append('id')  # Sicherstellen, dass das 'id'-Feld im Bearbeitungsmodus angezeigt wird
        else:
            fields = ["title", "description", "video_file", "genre"]  # Im Erstellmodus nur diese Felder
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["video_144p", "video_240p", "video_360p", "video_480p", "video_720p", "video_1080p"]
        if obj:
            readonly_fields.append('id')  
        return readonly_fields


