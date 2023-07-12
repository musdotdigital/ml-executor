from typing import Dict
from celery import Celery


def get_tasks(celery_app: Celery) -> Dict:
    """
    Get the current state of the Celery task queue.

    Parameters
    ----------
    celery_app : Celery
        Celery app instance

    Returns
    ----------
    Dict
        Dictionary containing the current state of the Celery task queue
    """

    # Get task queue state
    inspector = celery_app.control.inspect()

    scheduled = inspector.scheduled()
    active = inspector.active()
    reserved = inspector.reserved()

    tasks = {
        'scheduled': scheduled,
        'active': active,
        'reserved': reserved
    }

    return tasks


def ping_celery(celery_app: Celery) -> bool:
    """
    Check the status of Celery workers.

    Parameters
    ----------
    celery_app : Celery
        Celery app instance

    Returns
    ----------
    bool
        True if Celery workers are running, False otherwise
    """

    i = celery_app.control.inspect()
    return i.ping()
