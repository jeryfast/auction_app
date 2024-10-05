import pytest
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.core import mail
from rest_framework.test import APIClient
from auctions_app.models import Auction, Bid
from celery.result import AsyncResult
from decouple import config
from django.contrib.auth.models import User
from django.test import override_settings
from django.core.mail import get_connection
from django.conf import settings
from django.core.mail import send_mail
from django.core import mail
from django.test import override_settings
import pytest


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    return User.objects.create_user(username=config('TEST_USER_NAME'),
                                    password=config('TEST_USER_PASSWORD'),
                                    email=config('TEST_USER_EMAIL'))

@pytest.fixture
def create_user_to_bid(db):
    return User.objects.create_user(username=config('TEST_USER_NAME1'),
                                    password=config('TEST_USER_PASSWORD1'),
                                    email=config('TEST_USER_EMAIL1'))

@pytest.fixture
def create_auction(create_user):
    auction = Auction.objects.create(
        name="Test Auction",
        description="A test auction active for 1 day",
        starting_price=100.00,
        creator=create_user,
        start_time=timezone.now()
    )
    return auction


@pytest.mark.django_db
def test_email_backend():
    backend_name = get_connection().__class__.__name__
    print(f"Active Email Backend: {backend_name}")
    assert backend_name == 'LocmemBackend', f"Unexpected backend: {backend_name}"

    
@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_send_in_memory_email():
    # Send an email
    send_mail(
        'Test Subject',
        'Test message body',
        'from@example.com',
        ['to@example.com'],
    )

    # Access the in-memory email data via mail.outbox
    assert len(mail.outbox) == 1  # One email should be sent
    email = mail.outbox[0]  # Access the first email in the outbox

    # Check email content
    assert email.subject == 'Test Subject'
    assert email.body == 'Test message body'
    assert email.from_email == 'from@example.com'
    assert email.to == ['to@example.com']

    # Optionally, print the email content for debugging purposes
    print("Subject:", email.subject)
    print("Body:", email.body)
    print("From:", email.from_email)
    print("To:", email.to)

@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_auction_end_notifications(api_client, create_user_to_bid, create_auction):    
    # Simulate auction end (1 day later)
    auction = create_auction

    # Bid
    bid_user = create_user_to_bid
    print(f"Creating bid by user: {bid_user}")

    # Create a bid on the auction
    Bid.objects.create(
        auction=auction,
        user=bid_user,
        amount=150.00,
    )

    auction.start_time = timezone.now() - timedelta(days=1, minutes=1)
    auction.save()

    # Trigger auction end and get the Celery task IDs
    winner_task, creator_task = auction.end_auction()
    print(f"Winner task: {winner_task.id}, Creator task: {creator_task.id}")

    # Wait for the Celery tasks to complete
    AsyncResult(winner_task.id).get(timeout=2)
    AsyncResult(creator_task.id).get(timeout=2)

    # Check that emails were sent
    print(f"Emails in outbox: {len(mail.outbox)}")
    assert len(mail.outbox) == 2  # One email to the winner and one to the creator

    # Verify email subjects
    winner_email = mail.outbox[0]
    assert 'Congratulations! You\'ve won the auction!' in winner_email.subject

    creator_email = mail.outbox[1]
    assert 'Your auction has ended' in creator_email.subject


