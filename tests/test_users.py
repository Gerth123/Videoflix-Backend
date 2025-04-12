import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'videoflix_backend_hub.settings'

import django
django.setup()

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
    profile, _ = UserProfile.objects.get_or_create(user=create_user)
    return profile

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_user_registration(client):
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
    token = default_token_generator.make_token(create_user)
    uid = urlsafe_base64_encode(force_bytes(create_user.pk))
    activation_url = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})  

    response = client.get(activation_url)
    assert response.status_code == status.HTTP_302_FOUND  

@pytest.mark.django_db
def test_password_reset_request(client, create_user):
    url = reverse('password-reset-request')
    data = {
        "email": create_user.email
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "Falls die E-Mail existiert" in response.data["message"]

@pytest.mark.django_db
def test_password_reset_confirm(client, create_user):
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
    url = reverse('userprofile-detail', kwargs={'pk': create_user_profile.pk})  
    client.force_authenticate(user=create_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'email' in response.data

@pytest.mark.django_db
def test_user_profile_list(client, create_user, create_user_profile):
    url = reverse('userprofile-list') 
    client.force_authenticate(user=create_user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
