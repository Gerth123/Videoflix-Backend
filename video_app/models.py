import os
import ffmpeg
from datetime import date
from django.db import models
from django.core.files import File
from django.conf import settings

class Video(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(upload_to='videos/originals', blank=True, null=True)
    video_144p = models.FileField(upload_to='videos/144p', blank=True, null=True)
    video_240p = models.FileField(upload_to='videos/240p', blank=True, null=True)
    video_360p = models.FileField(upload_to='videos/360p', blank=True, null=True)
    video_480p = models.FileField(upload_to='videos/480p', blank=True, null=True)
    video_720p = models.FileField(upload_to='videos/720p', blank=True, null=True)
    video_1080p = models.FileField(upload_to='videos/1080p', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    def generate_thumbnail(self):
        if not self.video_file:
            return
        input_path = self.video_file.path
        output_filename = f"{self.id}.jpg"
        output_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            (
                ffmpeg.input(input_path, ss=1)  
                .output(output_path, vframes=1, format="image2", vcodec="mjpeg")
                .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            )
            with open(output_path, "rb") as file:
                self.thumbnail.save(output_filename, File(file), save=False)
        except Exception as e:
            print(f"⚠️ Fehler beim Erstellen des Thumbnails: {e}")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  

        if not self.thumbnail and self.video_file:
            self.generate_thumbnail()
            super().save(*args, **kwargs)  

    def __str__(self):
        return f"{self.id} - {self.title}"
    