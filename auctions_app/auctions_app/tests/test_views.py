import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from auctions_app.models import Auction, Bid
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from auctions_app.models import Auction
from django.utils import timezone
from PIL import Image
import tempfile
import io
import os
from decouple import config  # To use environment variables


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
        return User.objects.create_user(username=config('TEST_USER_NAME'),
                                    password=config('TEST_USER_PASSWORD'))

@pytest.mark.django_db
def test_user_creation(create_user):
    user = create_user
    print(User.objects.all())  # This will show you the users in the test database
    assert User.objects.count() == 1



@pytest.fixture
def create_auction(create_user):
    # Specify the path to the image file
    image_path = os.path.join(os.path.dirname(__file__), 'image.jpg')

    # Open the file in binary mode and use SimpleUploadedFile
    with open(image_path, 'rb') as img_file:
        image = SimpleUploadedFile('image.jpg', img_file.read(), content_type='image/jpeg')

        # Create the auction object with the real image
        auction = Auction.objects.create(
            name="Test Auction",
            description="A test auction",
            image=image,
            starting_price=100.00,
            creator=create_user,
            start_time=timezone.now()
        )

        return auction

### 3. **Test: Get List of Auctions**

@pytest.mark.django_db
def test_get_auctions_list(api_client, create_auction):
    url = reverse('auction-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1  # We expect one auction created

### 4. **Test: Get Auction Detail**

@pytest.mark.django_db
def test_get_auction_detail(api_client, create_auction):
    url = reverse('auction-detail', args=[create_auction.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == create_auction.name

### 5. **Test: Post a New Auction (Authenticated User)**

@pytest.mark.django_db
def test_post_auction_authenticated(api_client, create_user):
    # Obtain JWT token for the user
    url = reverse('token_obtain_pair')
    response = api_client.post(url, {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')
    assert response.status_code == 200
    token = response.data['access']

    # Set the token in the Authorization header
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Now make the POST request to create an auction
    url = reverse('auction-list')
    with open('auctions_app/tests/image.jpg', 'rb') as image_file:
        auction_data = {
            "name": "New Auction",
            "description": "This is a new auction",
            "image": image_file,
            "starting_price": 50.00,
        }
        response = api_client.post(url, auction_data, format='multipart')

    print(response.data)
    assert response.status_code == status.HTTP_201_CREATED





### 6. **Test: Post a New Auction (Unauthenticated User)**

@pytest.mark.django_db
def test_post_auction_unauthenticated(api_client):
    # No login here, so the user is unauthenticated
    url = reverse('auction-list')

    with open('auctions_app/tests/image.jpg', 'rb') as image_file:
        auction_data = {
            "name": "Unauthorized Auction",
            "description": "This is an unauthorized auction",
            "image": image_file,
            "starting_price": 100.00,
        }
        response = api_client.post(url, auction_data, format='multipart')

    print(response.data)
    # Assert that the unauthenticated user receives a 401 Unauthorized response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



### 7. **Test: Post a New Bid on an Auction**

@pytest.mark.django_db
def test_post_bid_on_auction(api_client, create_user, create_auction):
    # Log in to get the token
    login_url = reverse('token_obtain_pair')
    response = api_client.post(login_url, {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')
    token = response.data['access']

    # Add token to the headers
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    # Post a bid
    url = reverse('auction-bid', args=[create_auction.id])
    bid_data = {
        "amount": 150.00
    }
    response = api_client.post(url, bid_data, format='json')
    
    assert response.status_code == status.HTTP_200_OK


### 8. **Test: Get List of Bids for an Auction**

@pytest.mark.django_db
def test_get_auction_bids_list(api_client, create_auction):
    url = reverse('bid-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 0  # Assuming no bids yet



@pytest.fixture
def create_multiple_auctions(create_user):
    """Create multiple auction instances for testing filtering, ordering, and paging."""
    auction1 = Auction.objects.create(
        name="Auction 1", description="First auction", starting_price=100.00, creator=create_user
    )
    auction2 = Auction.objects.create(
        name="Auction 2", description="Second auction", starting_price=200.00, creator=create_user
    )
    auction3 = Auction.objects.create(
        name="Auction 3", description="Third auction", starting_price=300.00, creator=create_user
    )
    return [auction1, auction2, auction3]

@pytest.mark.django_db
def test_list_auctions_with_filtering_ordering_paging(api_client, create_user, create_multiple_auctions):
    # Log in the test user
    api_client.login(username=config('TEST_USER_NAME'), password=config('TEST_USER_PASSWORD'))


    url = reverse('auction-list')

    # Test filtering by name (case insensitive)
    response = api_client.get(url, {'name': 'Auction 1'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == 'Auction 1'

    # Test ordering by starting price (descending)
    response = api_client.get(url, {'page_size': 3,'ordering': '-starting_price'})
    assert response.status_code == status.HTTP_200_OK
    # The first auction should be the one with the highest starting price
    assert response.data['results'][0]['starting_price'] == '300.00'
    assert response.data['results'][1]['starting_price'] == '200.00'
    assert response.data['results'][2]['starting_price'] == '100.00'

    # Test pagination: only 2 results per page
    response = api_client.get(url, {'page': 1, 'page_size': 2})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2  # Only 2 auctions should be on the first page

    # Test the second page of results
    response = api_client.get(url, {'page': 2, 'page_size': 2})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1  # Only 1 auction should be on the second page



from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@pytest.mark.django_db
def test_redis_channel_layer():
    # Get the channel layer
    channel_layer = get_channel_layer()

    # Define a test channel and message
    test_channel = 'test_channel'
    test_message = {'type': 'test.message', 'text': 'Hello, Redis!'}

    # Send the message to the test channel using async_to_sync
    async_to_sync(channel_layer.send)(test_channel, test_message)

    # Try to receive the message from the channel layer
    received_message = async_to_sync(channel_layer.receive)(test_channel)

    # Assert that the received message matches what was sent
    assert received_message == test_message
