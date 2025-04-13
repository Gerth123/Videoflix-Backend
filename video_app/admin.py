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
        """
        Returns a list of field names that should be used for the video model when
        adding or changing a video instance in the admin interface.

        Parameters
        ----------
        request : django.http.HttpRequest
            The request from the client for the current view.
        obj : Video
            The video instance being changed, if any.

        Returns
        -------
        list
            The list of field names to display in the admin interface.
        """
        fields = [field.name for field in self.opts.model._meta.fields]
        if obj:
            fields.append('id')
        else:
            fields = ["title", "description", "video_file", "genre"]
        return fields

    def get_readonly_fields(self, request, obj=None):
        """
        Returns a list of field names that should be marked as readonly in the
        admin interface for the video model.

        Parameters
        ----------
        request : django.http.HttpRequest
            The request from the client for the current view.
        obj : Video
            The video instance being changed, if any.

        Returns
        -------
        list
            The list of readonly field names to mark as readonly in the admin
            interface.
        """
        readonly_fields = ["video_144p", "video_240p", "video_360p", "video_480p", "video_720p", "video_1080p"]
        if obj:
            readonly_fields.append('id')
        return readonly_fields
