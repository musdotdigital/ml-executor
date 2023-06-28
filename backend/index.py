import json
from flask import jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .api.job_routes import get_job_status, is_dockerfile_valid, submit_dockerfile
from .api.celery_routes import get_tasks, ping_celery
from .config.server import app
from .config.celery import celery_init_app
from .config.schemas import StatusType, BackendType


if app.config['BACKEND_TYPE'] == BackendType.LOCAL_SUBPROCESS:
    STORAGE_URI = "redis://localhost:6379"
else:
    STORAGE_URI = "redis://redis:6379"

# Register Celery app
celery_app = celery_init_app(app)

# Rate limit API endpoints
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"],
    storage_uri=STORAGE_URI,
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window"
)


@app.route('/submit', methods=['POST'])
def submit():
    """ 
    API endpoint to submit a job. It validates the Dockerfile content, stores it on disk, 
    and then queues the job for processing. It also maintains the job status in Redis.

    Args
    ----
    data : bytes
        Request body containing the Dockerfile content
    """

    # Get Dockerfile content from request
    dockerfile_content = request.data.decode('utf-8')

    if not dockerfile_content:
        return jsonify({'error': 'No Dockerfile provided'}), 400

    try:
        if not is_dockerfile_valid(dockerfile_content):
            return jsonify({'error': 'Invalid Dockerfile'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Submit job
    job_id = submit_dockerfile(dockerfile_content)
    return jsonify({'job_id': job_id}), 200


@app.route('/status', methods=['GET'])
def status():
    """
    API endpoint to check the status of a job. It fetches the job status from Redis using the job_id.

    Args
    ----
    job_id : str
        Unique identifier for the job
    """

    schema = StatusType()
    job_id = schema.load(request.args.to_dict())['job_id']
    job_data = get_job_status(job_id)

    if job_data is not None:
        return jsonify(json.loads(job_data.decode('utf-8'))), 200
    else:
        return jsonify({'error': 'Job not found'}), 404


@app.route('/celery/tasks', methods=['GET'])
@limiter.exempt
def tasks():
    """
    API endpoint to get the current state of the Celery task queue.
    """
    return jsonify(get_tasks(celery_app)), 200


@app.route('/celery/ping', methods=['GET'])
@limiter.exempt
def ping():
    """
    API endpoint to check the status of Celery workers.
    """
    if ping_celery(celery_app):
        return jsonify({'status': 'success', 'message': 'Celery worker(s) is running.'})
    else:
        return jsonify({'status': 'error', 'message': 'No running Celery worker(s) found.'})
