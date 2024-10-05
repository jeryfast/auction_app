# test_settings.py

from .settings import *  # Import everything from your base settings

# Force Django to use locmem or Anymail TestBackend during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# You can also try using Anymail's TestBackend
#EMAIL_BACKEND = 'anymail.backends.test.EmailBackend'

# Override any Anymail-related settings to prevent real emails
ANYMAIL = {
    'SENDGRID_API_KEY': 'test-api-key',  # Ensure dummy key for SendGrid during testing
}

# In test_settings.py or override settings in the test
CELERY_TASK_ALWAYS_EAGER = True  # Make tasks run synchronously in tests
CELERY_TASK_EAGER_PROPAGATES = True  # Raise exceptions if tasks fail

