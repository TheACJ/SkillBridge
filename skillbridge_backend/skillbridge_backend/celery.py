"""
Celery configuration for SkillBridge backend.
This module contains the Celery application configuration and task definitions.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillbridge_backend.settings')

app = Celery('skillbridge_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    # Clean up old notifications (run daily at 2 AM)
    'cleanup-old-notifications': {
        'task': 'notifications.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=2, minute=0),
    },

    # Update roadmap progress based on GitHub activity (run every 6 hours)
    'update-roadmap-progress': {
        'task': 'progress.tasks.update_roadmap_progress_from_github',
        'schedule': crontab(minute=0, hour='*/6'),
    },

    # Award badges based on achievements (run daily at 3 AM)
    'award-achievement-badges': {
        'task': 'badges.tasks.award_achievement_badges',
        'schedule': crontab(hour=3, minute=0),
    },

    # Send session reminders (run every hour)
    'send-session-reminders': {
        'task': 'matches.tasks.send_session_reminders',
        'schedule': crontab(minute=0, hour='*'),
    },

    # Generate weekly progress reports (run every Monday at 9 AM)
    'generate-weekly-reports': {
        'task': 'progress.tasks.generate_weekly_progress_reports',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}

# Configure Celery settings
app.conf.update(
    # Task routing
    task_routes={
        'notifications.tasks.*': {'queue': 'notifications'},
        'progress.tasks.*': {'queue': 'progress'},
        'badges.tasks.*': {'queue': 'badges'},
        'matches.tasks.*': {'queue': 'matches'},
        'roadmaps.tasks.*': {'queue': 'roadmaps'},
    },

    # Task time limits
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes

    # Result backend settings
    result_expires=3600,  # 1 hour

    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,

    # Error handling
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f'Request: {self.request!r}')