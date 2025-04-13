import os
import ffmpeg
from datetime import date
from django.db import models
from django.core.files import File
from django.conf import settings
from django.utils.text import slugify


def get_unique_filename(target_dir, base_name, resolution, ext):
    """
    Generates a unique filename by appending a counter to the base name if needed.

    This function constructs a file path using the provided directory, base name,
    resolution, and file extension. If a file with the constructed name already
    exists in the directory, the function appends a counter to the base name to
    ensure uniqueness.

    Parameters
    ----------
    target_dir : str
        The directory where the file will be stored.
    base_name : str
        The base name for the file.
    resolution : str
        The resolution of the file (e.g., '144p', '720p').
    ext : str
        The file extension (e.g., '.mp4', '.webm').

    Returns
    -------
    str
        A unique file path constructed from the given parameters.
    """
    file_path = os.path.join(target_dir, f"{base_name}.{resolution}{ext}")
    counter = 1
    while os.path.exists(file_path):
        file_path = os.path.join(
            target_dir, f"{base_name}_{counter}.{resolution}{ext}")
        counter += 1
    return file_path


GENRE_CHOICES = [
    ('action', 'Action'),
    ('drama', 'Drama'),
    ('sci-fi', 'Sci-Fi'),
    ('documentary', 'Documentary'),
]


class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=500)
    video_file = models.FileField(
        upload_to='videos/originals', blank=True, null=True)
    video_144p = models.FileField(
        upload_to='videos/144p', blank=True, null=True)
    video_240p = models.FileField(
        upload_to='videos/240p', blank=True, null=True)
    video_360p = models.FileField(
        upload_to='videos/360p', blank=True, null=True)
    video_480p = models.FileField(
        upload_to='videos/480p', blank=True, null=True)
    video_720p = models.FileField(
        upload_to='videos/720p', blank=True, null=True)
    video_1080p = models.FileField(
        upload_to='videos/1080p', blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='thumbnails/', blank=True, null=True)
    genre = models.CharField(
        max_length=30, choices=GENRE_CHOICES, default='action')

    def generate_thumbnail(self):
        """
        Generates a thumbnail for the video.

        If the video file or the thumbnail already exists, this method does nothing.

        :raises ffmpeg.Error: If an error occurs while generating the thumbnail.
        """
        if not self.video_file or not self.id or self.thumbnail:
            return
        output_filename = f"{self.id}.jpg"
        output_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            (
                ffmpeg.input(self.video_file.path, ss=1)
                .output(output_path, vframes=1, format="image2", vcodec="mjpeg")
                .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            )
            self.thumbnail.name = f"thumbnails/{output_filename}"
        except ffmpeg.Error as e:
            print(f"⚠️ ffmpeg stderr:\n{e.stderr.decode()}")
            print(f"⚠️ Fehler beim Erstellen des Thumbnails: {e}")

    def save(self, *args, **kwargs):
        """
        Saves the video instance and its associated files.

        If the instance is being created and a video file is provided, this method
        renames the video file to ensure uniqueness by appending a counter to the
        slugified title. The thumbnail is generated after the instance is saved.

        :param args: Additional positional arguments passed to the parent's save method.
        :param kwargs: Additional keyword arguments passed to the parent's save method.
        """
        creating = self._state.adding and not self.pk
        if creating and self.video_file:
            safe_title = slugify(self.title)
            ext = os.path.splitext(self.video_file.name)[1]
            target_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'originals')
            os.makedirs(target_dir, exist_ok=True)
            unique_filename = get_unique_filename(target_dir, safe_title, 'original', ext)
            self.video_file.name = os.path.relpath(unique_filename, settings.MEDIA_ROOT)
        super().save(*args, **kwargs)
        if not self.thumbnail and self.video_file:
            self.generate_thumbnail()
            super().save(update_fields=["thumbnail"])

    def __str__(self):
        """
        Returns a string representation of the video instance.

        The string representation includes the video's id and title, separated by a hyphen.

        :return: A string representation of the video instance.
        """
        return f"{self.id} - {self.title}"
