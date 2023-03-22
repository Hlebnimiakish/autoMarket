"""This module contains celery config and celery app instance,
and celery beat schedule parameters"""

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

app = Celery(os.getenv('CELERY_APP'))

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Standard celery debug function"""
    print(f'Request: {self.request}')


app.conf.beat_schedule = {
    'evaluate_best_sellers_for_dealers_every_hour': {
        'task': 'find_suit_sellers_for_dealers',
        'schedule': 3600.0,
    },
    'purchase_cars_for_dealers_from_sellers_every_ten_minutes': {
        'task': "purchase_cars_for_dealers",
        'schedule': 600.0,
    },
}
