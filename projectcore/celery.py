import os
from celery import Celery

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectCore.settings')

app = Celery('ProjectCore')#change projectcore with ur project name
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() #to make all the tasks auto detected