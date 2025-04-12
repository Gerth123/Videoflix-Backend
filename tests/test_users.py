import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from users_app.models import UserProfile
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.crypto import get_random_string
from django.core.cache import cache
import random


@pytest.fixture
def create_user():
    """
    Fixture to create a new User instance with a unique username and email.
    The user is created with a default password "password123".
    Returns the created User object.
    """
    return User.objects.create_user(
        username=f'testuser{random.randint(1000, 9999)}',
        email=f"testuser{random.randint(1000, 9999)}@example.com",
        password="password123"
    )


@pytest.fixture
def create_user_profile(create_user):
    """
    Fixture to create a new UserProfile instance for a given User instance.
    If the UserProfile does not exist, it is created. Otherwise, the existing
    profile is returned.

    Args:
        create_user (fixture): Fixture to create a new User instance.

    Returns:
        UserProfile: The created or existing UserProfile instance.
    """
    profile, _ = UserProfile.objects.get_or_create(user=create_user)
    return profile


@pytest.fixture
def client():
    """
    Fixture to create a new instance of the Django Rest Framework's APIClient.
    This client can be used to make requests to the API endpoints.
    """
    return APIClient()


@pytest.mark.django_db
def test_user_registration(client):
    """
    Test the user registration endpoint.

    This test sends a POST request to the /registration/ endpoint with a valid
    email and password. It asserts that the response status code is 200 OK and
    that the response contains a 'toast_message' and 'username' key.
    """

    url = reverse('registration')
    data = {
        "email": "newuser@example.com",
        "password": "password123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'toast_message' in response.data
    assert 'username' in response.data


@pytest.mark.django_db
def test_login_with_email_and_password(client, create_user):
    """
    Test the login endpoint with an email and password.

    This test sends a POST request to the /login/ endpoint with a valid email
    and password. It asserts that the response status code is 200 OK and that
    the response contains a 'token' key, and that the email in the response
    matches the one used in the request.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
    """
    url = reverse('login')
    data = {
        "email": create_user.email,
        "password": "password123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.data
    assert response.data['email'] == create_user.email


@pytest.mark.django_db
def test_activate_account(client, create_user):
    """
    Test the account activation endpoint.

    This test sends a GET request to the /activate/<uidb64>/<token>/ endpoint
    with valid UID and token parameters. It asserts that the response status
    code is 302 FOUND, indicating a successful redirection after account
    activation.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
    """

    token = default_token_generator.make_token(create_user)
    uid = urlsafe_base64_encode(force_bytes(create_user.pk))
    activation_url = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})

    response = client.get(activation_url)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_password_reset_request(client, create_user):
    """
    Test the password reset request endpoint.

    This test sends a POST request to the /auth/password-reset/ endpoint with a
    valid email. It asserts that the response status code is 200 OK and that the
    response message indicates an email has been sent if the email exists.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
    """

    url = reverse('password-reset-request')
    data = {
        "email": create_user.email
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "Falls die E-Mail existiert" in response.data["message"]


@pytest.mark.django_db
def test_password_reset_confirm(client, create_user):
    """
    Test the password reset confirm endpoint.

    This test sends a POST request to the /auth/password-reset/confirm/ endpoint
    with a valid token and new password. It asserts that the response status code
    is 200 OK and that the user's password has been updated.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
    """
    token = get_random_string(50)
    cache.set(f"password_reset_{token}", create_user.id, timeout=3600)

    url = reverse('password-reset-confirm')
    data = {
        "token": token,
        "password": "newpassword123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    create_user.refresh_from_db()
    assert create_user.check_password("newpassword123")


@pytest.mark.django_db
def test_user_profile_detail(client, create_user, create_user_profile):
    """
    Test the user profile detail endpoint.

    This test sends a GET request to the /profiles/{pk}/ endpoint with a valid
    user profile ID. It asserts that the response status code is 200 OK and that
    the response contains a User object with the expected fields.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
        create_user_profile (fixture): Fixture to create a new User Profile
            instance with a random color and phone number.
    """
    url = reverse('userprofile-detail', kwargs={'pk': create_user_profile.pk})
    client.force_authenticate(user=create_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'email' in response.data


@pytest.mark.django_db
def test_user_profile_list(client, create_user, create_user_profile):
    """
    Test the user profile list endpoint.

    This test sends a GET request to the /profiles/ endpoint to retrieve a list
    of user profiles. It asserts that the response status code is 200 OK and
    that the returned data contains at least one user profile.

    Args:
        client (fixture): Fixture to create a new instance of the Django Rest
            Framework's APIClient.
        create_user (fixture): Fixture to create a new User instance with a
            unique username and email.
        create_user_profile (fixture): Fixture to create a new UserProfile
            instance for the created user.
    """

    url = reverse('userprofile-list')
    client.force_authenticate(user=create_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
