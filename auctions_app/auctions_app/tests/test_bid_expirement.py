import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from auctions_app.models import Auction, Bid
from decouple import config  # To use environment variables
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
        return User.objects.create_user(username=config('TEST_USER_NAME'),
                                    password=config('TEST_USER_PASSWORD'))

@pytest.fixture
def create_auction(create_user):
    # Create an auction with the current time as the start time
    auction = Auction.objects.create(
        name="Test Auction",
        description="A test auction active for 1 day",
        starting_price=100.00,
        creator=create_user,
        start_time=timezone.now()
    )
    return auction

@pytest.mark.django_db
def test_auction_active_for_one_day(api_client, create_user, create_auction):
    # Obtain JWT token for the user
    login_url = reverse('token_obtain_pair')
    response = api_client.post(login_url,  {
        'username': config('TEST_USER_NAME'),
        'password': config('TEST_USER_PASSWORD')
    }, format='json')

    assert response.status_code == 200
    token = response.data['access']
    
    # Set token in the headers
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    auction = create_auction

    # Define the URL for placing a bid
    bid_url = reverse('auction-bid', args=[auction.id])

    # 1. Test: Bid within the first 24 hours (active auction)
    bid_data = {"amount": 150.00}
    response = api_client.post(bid_url, bid_data, format='json')
    
    # Assert the bid is accepted during the active period
    assert response.status_code == status.HTTP_200_OK
    
     # Retrieve the highest bid (ordered by amount in descending order)
    highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()

    # Assert the highest bid matches the bid placed
    assert highest_bid.amount == 150.00

    # 2. Test: Bid after auction expiration (1 day later)
    # Simulate the passage of time by advancing the auction's start time by 24 hours
    auction.start_time = timezone.now() - timedelta(days=1, minutes=1)
    auction.save()

    # Try to place a bid after the auction has ended
    bid_data = {"amount": 200.00}
    response = api_client.post(bid_url, bid_data, format='json')

    # Retrieve the highest bid (ordered by amount in descending order)
    highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()

    # Assert the highest bid matches the bid placed
    assert highest_bid.amount == 150.00
    
    # Assert that the bid is rejected after the auction has ended
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Auction is closed." in str(response.data)  # Customize error message as needed
