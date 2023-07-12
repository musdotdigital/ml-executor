import re
import os
import uuid
import json
import subprocess
import logging
from redis import Redis
from docker import DockerClient
from celery import shared_task

from ..config.server import DOCKERFILE_FOLDER

# Create abstraction for Redis
redis = Redis()

# Create Docker client
client = DockerClient.from_env()


@shared_task
def run_job(job_id: str):
    """
    Asynchronous Celery task that handles the building and running of a Docker image.
    It also captures the performance of the Docker container.

    Parameters
    ----------
    job_id : str
        Unique identifier for the job
    """

    logging.info(f'Running job {job_id}')

    # Create data directory if it does not exist
    dockerfile_dir = os.path.join(
        os.getcwd(), f'{DOCKERFILE_FOLDER}/{job_id}')

    os.makedirs(f'{dockerfile_dir}/data', exist_ok=True)

    # Build and check vulnerabilities of Docker image
    try:
        logging.info(f'Building image {job_id}')
        image, _ = client.images.build(path=dockerfile_dir, tag=job_id)

        # Check if image has any high vulnerabilities
        scan_result = scan_image(image.id)
        if not scan_result:
            logging.error(f'Vulnerability scan failed for image {image.id}')
            redis.set(job_id, json.dumps(
                {'status': 'failed', 'error': 'Vulnerability scan failed'}))
            return

    except Exception as e:
        logging.error(f'Error building image {job_id}: {e}')
        redis.set(job_id, json.dumps({'status': 'failed', 'error': str(e)}))
        return

    # Run Docker container
    try:
        logging.info(f'Running container {image.id}')
        client.containers.run(image.id,
                              user="nobody",
                              cap_drop=["ALL"],
                              volumes={
                                  f'{dockerfile_dir}/data': {'bind': '/data', 'mode': 'rw'}}, 
                              auto_remove=True, 
                              detach=True)

    except Exception as e:
        logging.error(f'Error running container {image.id}: {e}')
        redis.set(job_id, json.dumps({'status': 'failed', 'error': str(e)}))
        return

    # Extract performance
    try:
        with open(f'{dockerfile_dir}/data/perf.json', 'r') as f:
            perf = json.load(f)['perf']

    except Exception as e:
        logging.error(
            f'Error extracting performance for container {image.id}: {e}')
        redis.set(job_id, json.dumps({'status': 'failed', 'error': str(e)}))
        return

    # Update job status and performance
    logging.info(f'Job {job_id} completed successfully, performance: {perf}')
    redis.set(job_id, json.dumps({'status': 'success', 'performance': perf}))


def submit_dockerfile(dockerfile_content: str) -> str:
    '''
    Function to submit a job. It validates the Dockerfile content, stores it on disk,
    and then queues the job for processing. It also maintains the job status in Redis.  

    Returns
    -------
    job_id : str
        Unique identifier for the job
    '''

    # Generate unique identifier for job
    job_id = str(uuid.uuid4())

    # Create directory if it does not exist
    os.makedirs(f'./{DOCKERFILE_FOLDER}/{job_id}', exist_ok=True)

    # Save Dockerfile to a file
    with open(f'./{DOCKERFILE_FOLDER}/{job_id}/Dockerfile', '+w') as f:
        f.write(dockerfile_content)

    # Set job status to processing
    redis.set(job_id, json.dumps({'status': 'processing'}))

    # Run job asynchronously on Celery Worker
    run_job.delay(job_id)

    logging.info(f'Submitted job {job_id} for dockerfile: {dockerfile_content}')
    return job_id



def get_job_status(job_id: str) -> bytes | None:
    '''
    Function to get the status of a job from Redis.

    Returns
    -------
    job_status : bytes | None
        Status of the job
    '''
   
    job_status = redis.get(job_id)

    logging.info(f'Job {job_id} status: {job_status}')
    return job_status


def validate_dockerfile(dockerfile_content: str) -> bool:
    """
    Function to validate the content of a Dockerfile. It checks for any forbidden commands.
    """

    forbidden_commands = ["USER root", "ADD . /", "COPY . /"]
    for command in forbidden_commands:
        if command in dockerfile_content:
            return False

    logging.info('Dockerfile validation successful')
    return True


def scan_image(image_id: str) -> bool:
    """
    Function to scan a Docker image for vulnerabilities using Trivy.

    Parameters
    ----------
    image_id : str
        Unique identifier for the Docker image

    Returns
    -------
    scan_result : bool
        Result of the vulnerability scan
    """

    result = subprocess.run(
        ['trivy', 'image', image_id], stdout=subprocess.PIPE)
    logging.info(f'Vulnerability scan result: {result.stdout.decode("utf-8")}')

    # Extract the number of high vulnerabilities
    high_vulnerabilities = re.search(
        r'HIGH: (\d+)', result.stdout.decode('utf-8'))

    # Check if the number of high vulnerabilities is more than 0
    logging.info(f'High vulnerabilities: {int(high_vulnerabilities.group(1))}')
    if high_vulnerabilities and int(high_vulnerabilities.group(1)) > 0:
        return False

    logging.info('No high vulnerabilities found')
    return True
