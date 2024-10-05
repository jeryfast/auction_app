import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decouple import config
from django.contrib.auth.models import User

@pytest.fixture
def create_user(db):
        return User.objects.create_user(username=config('TEST_USER_NAME'),
                                    password=config('TEST_USER_PASSWORD'))

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_authenticated_access(api_client, create_user):
    # Obtain JWT token for the user
    login_url = reverse('token_obtain_pair')
    response = api_client.post(login_url, {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')

    # Assert token was successfully obtained
    assert response.status_code == 200
    token = response.data['access']

    # Set the token in the Authorization header
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Access a protected endpoint
    url = reverse('auction-list')  # Assuming auction-list is a protected endpoint
    response = api_client.get(url)

    # Assert that the authenticated user receives a 200 OK response
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_invalid_token(api_client):
    # Set an invalid token in the Authorization header
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')

    # Attempt to access a protected endpoint
    url = reverse('auction-list')
    response = api_client.get(url)

    # Assert that the response status is 401 Unauthorized
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_expired_token(api_client, create_user):
    # Obtain JWT token for the user
    login_url = reverse('token_obtain_pair')
    response = api_client.post(login_url, {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')

    # Assert token was successfully obtained
    assert response.status_code == 200
    token = response.data['access']

    expired_token = token[:-1]  # Manipulate the token to simulate expiration (this is just an example, actual implementation depends on your JWT settings)
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + expired_token)

    # Attempt to access a protected endpoint
    url = reverse('auction-list')
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED



@pytest.mark.django_db
def test_valid_token_vs_invalid_token(api_client, create_user):
    # Obtain valid JWT token
    login_url = reverse('token_obtain_pair')
    response = api_client.post(login_url, {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')
    valid_token = response.data['access']

    # Set valid token in the Authorization header
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + valid_token)
    url = reverse('auction-list')
    valid_response = api_client.get(url)

    # Assert that the valid token gives 200 OK
    assert valid_response.status_code == status.HTTP_200_OK

    # Set invalid token in the Authorization header
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalid_token')
    invalid_response = api_client.get(url)

    # Assert that the invalid token gives 401 Unauthorized
    assert invalid_response.status_code == status.HTTP_401_UNAUTHORIZED
