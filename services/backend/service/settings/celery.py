import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

USE_CELERY = bool(int(os.environ.get('USE_CELERY', '0')))

if USE_CELERY:
    from celery import Celery

    app = Celery('app')
    app.config_from_object('django.conf:settings', namespace='CELERY')

    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

    @app.task(bind=True)
    def debug_task(self):
        print(f'Request: {self.request!r}')

else:
    # Provide a lightweight stub object so imports like
    # `from settings.celery import debug_task` and calls to
    # `debug_task.delay()` won't fail when Celery is disabled.
    class _DisabledTask:
        def delay(self, *args, **kwargs):
            # no-op when celery disabled
            return None

    debug_task = _DisabledTask()
