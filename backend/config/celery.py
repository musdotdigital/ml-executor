from celery import Celery, Task
from flask import Flask

from .schemas import BackendType

LOCAL_CELERY_URL = "redis://localhost:6379/0"
REDIS_CELERY_URL = "redis://redis:6379/0"


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)

    app.extensions["celery"] = celery_app

    if app.config['BACKEND_TYPE'] == BackendType.LOCAL_SUBPROCESS:
        CELERY_URL = LOCAL_CELERY_URL
    else:
        CELERY_URL = REDIS_CELERY_URL

    app.config.from_mapping(
        CELERY=dict(
            broker_url=CELERY_URL,
            result_backend=CELERY_URL,
            task_ignore_result=True,
        ),
    )

    celery_app.set_default()
    celery_app.config_from_object(app.config["CELERY"])

    return celery_app
