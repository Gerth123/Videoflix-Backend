from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from video_app.models import Video
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


class VideoAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='adminpass')
        self.client.login(username='admin', password='adminpass')

        video_file = SimpleUploadedFile("test.mp4", b"file_content", content_type="video/mp4")

        self.video = Video.objects.create(
            title="Test Video",
            genre="Action",
            video_480p=video_file,
            video_720p=video_file,
            thumbnail=video_file
        )

    def test_list_videos(self):
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_detail(self):
        url = reverse('video-detail', args=[self.video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_with_resolution(self):
        url = reverse('video-detail', args=[self.video.id]) + "?resolution=480p"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('video_url', response.data)

    def test_get_video_with_invalid_resolution(self):
        url = reverse('video-detail', args=[self.video.id]) + "?resolution=999p"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_video(self):
        url = reverse('video-detail', args=[self.video.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_thumbnail(self):
        url = reverse('video-thumbnail', args=[self.video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('thumbnail_url', response.data)

    def test_thumbnail_not_found(self):
        video = Video.objects.create(title="No Thumb", genre="Drama")
        url = reverse('video-thumbnail', args=[video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_genre_grouped_videos(self):
        url = reverse('genres-grouped')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("New on Videoflix" in group["name"] for group in response.data))

    def test_big_thumbnail_view(self):
        url = reverse('big-thumbnail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
