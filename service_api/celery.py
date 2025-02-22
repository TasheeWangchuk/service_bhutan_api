from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from ssl import CERT_NONE
from dotenv import load_dotenv

load_dotenv()

# # set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service_api.settings")


app = Celery(
    "service_api",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    broker_use_ssl={
        'ssl_cert_reqs': CERT_NONE,  # or CERT_REQUIRED, CERT_OPTIONAL
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': CERT_NONE,  # or CERT_REQUIRED, CERT_OPTIONAL
    },
)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

