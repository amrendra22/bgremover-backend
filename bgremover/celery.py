import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bgremover.settings')

# Create Celery app
app = Celery('bgremover')

# Load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicit SSL settings for rediss:// URLs
app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': 'CERT_NONE'
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': 'CERT_NONE'
    },
)

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

