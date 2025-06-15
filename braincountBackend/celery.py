import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'braincountBackend.settings')

app = Celery('braincountBackend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure the periodic tasks
app.conf.beat_schedule = {
    'update-impressions-hourly': {
        'task': 'api.tasks.update_impressions_hourly',
        'schedule': crontab(minute=0),  # Run at the start of every hour
    },
}

# Set max interval to 1 hour (3600 seconds)
app.conf.beat_max_loop_interval = 5400

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 