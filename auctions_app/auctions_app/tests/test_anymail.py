import pytest
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from anymail.message import AnymailMessage
from django.core import mail
from rest_framework.test import APIClient
from auctions_app.models import Auction, Bid
from decouple import config  # To use environment variables
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
        return User.objects.create_user(username=config('TEST_USER_NAME'),
                                    password=config('TEST_USER_PASSWORD'),
                                    email=config('SENDGRID_FROM'))

@pytest.fixture
def create_user_to_bid(db):
        return User.objects.create_user(username=config('TEST_USER_NAME1'),
                                    password=config('TEST_USER_PASSWORD1'),
                                    email=config('SENDGRID_FROM'))

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
def test_auction_end_notifications(api_client, create_user_to_bid, create_auction):
    # Simulate auction end (1 day later)
    auction = create_auction

    # Bid
    bid_user = create_user_to_bid
    print(bid_user)
    
    # Create a bid on the auction
    Bid.objects.create(
        auction=auction,
        user=bid_user,
        amount=150.00,
    )

    auction.start_time = timezone.now() - timedelta(days=1, minutes=1)
    auction.save()

    # Trigger auction end (either via view or model directly)
    auction.end_auction()

    # Check that emails were sent
    assert len(mail.outbox) == 2  # One email to the winner and one to the creator

    # Verify email subjects
    winner_email = mail.outbox[0]
    assert 'Congratulations! You\'ve won the auction!' in winner_email.subject

    creator_email = mail.outbox[1]
    assert 'Your auction has ended' in creator_email.subject
