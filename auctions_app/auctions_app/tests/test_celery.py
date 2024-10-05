from auctions_app.tasks import send_auction_winner_email
import pytest
from celery.result import AsyncResult

@pytest.mark.django_db
def test_celery_task_processing():
    # Trigger the Celery task
    result = send_auction_winner_email.delay(
        winner_email="winner@example.com",
        winner_username="winner",
        auction_name="Test Auction"
    )

    # Wait for the task result using Redis as the result backend
    result.get(timeout=10)  # Wait up to 10 seconds for the task to finish

    # Check that the task succeeded
    assert result.successful(), "The task failed or was not processed by Celery"
