import pathlib
from abc import ABC
from datetime import timedelta

from celery import Celery
from kombu import Queue
from celery import Task

from app import app as flask_app
from app.common.logging import set_logger_config
from app.extensions import db, logger
from asynctask.loader import TaskDirsLoader, AsyncTaskLoader


def init_celery(_app):
    class ContextTask(Task, ABC):
        def __call__(self, *args, **kwargs):
            with _app.app_context():
                set_logger_config('celery')
                result = None
                try:
                    result = super(ContextTask, self).__call__(*args, **kwargs)
                    db.session.close()
                except Exception as e:
                    db.session.rollback()
                    db.session.close()
                    logger.exception(e)

                return result

        def on_retry(self, exc, task_id, args, kwargs, einfo):
            super(ContextTask, self).on_retry(exc, task_id, args, kwargs, einfo)

        def on_success(self, retval, task_id, args, kwargs):
            super(ContextTask, self).on_success(retval, task_id, args, kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            super(ContextTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    base_dir = pathlib.Path(__name__).parent
    task_dirs_loader = [TaskDirsLoader(base_dir, 'tasks')]

    task_dir = AsyncTaskLoader(
        task_dirs_loader, base_dir
    ).generate_load_path()

    config = _app.config.copy()
    _celery = Celery(
        __name__,
        task_cls=ContextTask,
        backend=config['CELERY_RESULT_BACKEND'],
        broker=config['CELERY_BROKER_URL'],
        include=task_dir,
    )
    _celery.conf.update(
        timezone='Asia/Shanghai',
        beat_schedule={
            'event_polling': {
                'task': 'app.tasks.event_schedule.event_polling',
                'schedule': timedelta(minutes=1)
            }
        },
        task_default_queue='default',
        task_queues=(
            Queue('default', routing_key='app.#'),
        ),
        task_default_exchange_type='direct',
        task_default_routing_key='tasks.default',
        task_routes=([('app.*', {'queue': 'default'}), ],),
        broker_transport_options={
            'max_retries': 3,
            'interval_start': 0,
            'interval_step': 0.2,
            'interval_max': 0.2,
        },
        broker_heartbeat=0,
        worker_max_tasks_per_child=20,
    )

    return _celery


celery = init_celery(flask_app)
