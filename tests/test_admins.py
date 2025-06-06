import pytest
from django.contrib.admin.sites import AdminSite
from video_app.admin import VideoAdmin
from video_app.models import Video
from django.contrib.auth.models import User


class DummyRequest:
    pass


@pytest.mark.django_db
def test_get_fields_add_mode():
    """
    Tests that the get_fields method returns the correct fields for adding a video.
    """

    video_admin = VideoAdmin(Video, AdminSite())
    fields = video_admin.get_fields(DummyRequest(), obj=None)
    assert fields == ["title", "description", "video_file", "genre"]


@pytest.mark.django_db
def test_get_fields_change_mode():
    """
    Tests that the get_fields method returns the correct fields for changing a video.
    For changing a video, the 'id' field should be included and the 'title' field should be included.
    """

    video_admin = VideoAdmin(Video, AdminSite())
    video = Video.objects.create(title="Test", description="desc", video_file="test.mp4", genre="Drama")
    fields = video_admin.get_fields(DummyRequest(), obj=video)
    assert 'id' in fields
    assert 'title' in fields


@pytest.mark.django_db
def test_get_readonly_fields_add_mode():
    """
    Tests that the get_readonly_fields method returns the correct readonly fields when adding a video.
    For adding a video, the readonly fields should include various resolution fields.
    """

    video_admin = VideoAdmin(Video, AdminSite())
    readonly_fields = video_admin.get_readonly_fields(DummyRequest(), obj=None)
    expected_fields = ["video_144p", "video_240p", "video_360p", "video_480p", "video_720p", "video_1080p"]
    assert readonly_fields == expected_fields


@pytest.mark.django_db
def test_get_readonly_fields_change_mode():
    """
    Tests that the get_readonly_fields method returns the correct readonly fields when changing a video.
    For changing a video, the readonly fields should include various resolution fields and the 'id' field.
    """

    video_admin = VideoAdmin(Video, AdminSite())
    video = Video.objects.create(title="Test", description="desc", video_file="test.mp4", genre="Drama")
    readonly_fields = video_admin.get_readonly_fields(DummyRequest(), obj=video)
    assert 'id' in readonly_fields
