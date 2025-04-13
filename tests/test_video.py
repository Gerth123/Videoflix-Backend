from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from video_app.models import Video
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


class VideoAPITestCase(APITestCase):

    def setUp(self):
        """
        Set up a test video and log in as admin user.

        Set up a test video with title "Test Video", genre "Action" and video files in 480p and 720p resolutions.
        The video thumbnail is set to the same as the video file.
        The admin user is logged in for authentication.
        """
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
        """
        Test that the video list endpoint returns a 200 status code.

        This test ensures that the video list endpoint is working correctly and
        returns the expected status code of 200.
        """
        url = reverse('video-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_detail(self):
        """
        Test that the video detail endpoint returns a 200 status code.

        This test ensures that the video detail endpoint is working correctly and
        returns the expected status code of 200.
        """
        url = reverse('video-detail', args=[self.video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_video_with_resolution(self):
        """
        Test that the video detail endpoint returns a 200 status code and contains 'video_url'
        when a valid resolution is provided.

        This test ensures that the video detail endpoint functions correctly when a valid
        resolution is specified in the query parameters and returns the expected status code
        of 200, along with a 'video_url' in the response data.
        """
        url = reverse('video-detail', args=[self.video.id]) + "?resolution=480p"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('video_url', response.data)

    def test_get_video_with_invalid_resolution(self):
        """
        Test that the video detail endpoint returns a 400 status code when an invalid resolution is provided.

        This test ensures that the video detail endpoint functions correctly when an invalid resolution
        is specified in the query parameters and returns the expected status code of 400.
        """
        url = reverse('video-detail', args=[self.video.id]) + "?resolution=999p"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_video(self):
        """
        Test that the video detail endpoint returns a 204 status code when a video is deleted.

        This test ensures that the video detail endpoint functions correctly when a video is deleted
        and returns the expected status code of 204.
        """
        url = reverse('video-detail', args=[self.video.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_thumbnail(self):
        """
        Test that the video thumbnail endpoint returns a 200 status code and contains 'thumbnail_url'
        when a valid video id is provided.

        This test ensures that the video thumbnail endpoint functions correctly when a valid video id is specified in
        the url parameters and returns the expected status code of 200,
        along with a 'thumbnail_url' in the response data.
        """
        url = reverse('video-thumbnail', args=[self.video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('thumbnail_url', response.data)

    def test_thumbnail_not_found(self):
        """
        Test that the video thumbnail endpoint returns a 404 status code when a video is
        requested that does not have a thumbnail associated with it.

        This test ensures that the video thumbnail endpoint functions correctly when a
        video is requested that does not have a thumbnail associated with it and returns
        the expected status code of 404.
        """

        video = Video.objects.create(title="No Thumb", genre="Drama")
        url = reverse('video-thumbnail', args=[video.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_genre_grouped_videos(self):
        """
        Test that the genre grouped videos endpoint returns a 200 status code and contains 'New on Videoflix'
        in the response data.

        This test ensures that the genre grouped videos endpoint functions correctly and returns the expected
        status code of 200, along with a 'New on Videoflix' group in the response data.
        """
        url = reverse('genres-grouped')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any("New on Videoflix" in group["name"] for group in response.data))

    def test_big_thumbnail_view(self):
        """
        Test that the big thumbnail view endpoint returns a 200 status code and contains 'title' in the response data.

        This test ensures that the big thumbnail view endpoint functions correctly and returns the expected status
        code of 200, along with a 'title' in the response data.
        """
        url = reverse('big-thumbnail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
