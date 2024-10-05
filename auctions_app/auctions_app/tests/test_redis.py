import redis
from django.conf import settings
import pytest

@pytest.mark.django_db
def test_redis_connection():
    # Create a Redis connection using the URL from your settings (e.g., CELERY_BROKER_URL or CHANNEL_LAYERS)
    redis_client = redis.StrictRedis.from_url(settings.CELERY_BROKER_URL)

    # Set a test key-value pair in Redis
    redis_client.set('test_key', 'test_value')

    # Get the value of the test key
    value = redis_client.get('test_key').decode('utf-8')

    # Assert that Redis returned the expected value
    assert value == 'test_value', "Redis did not return the expected value."

    # Print success message for debugging purposes
    print("Redis connection test passed!")
