import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the celery instance and configure it using the settings from Django
app = Celery('config')

app = Celery('config')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()

# Schedule the anomaly detection task to run hourly
app.conf.beat_schedule = {
    'detect-anomalies': {
        'task': 'ip_tracking.tasks.detect_anomalies',
        'schedule': crontab(minute=0),  # Run at the start of every hour
    },
}