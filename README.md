# ML Executor

Flask API service that receives and executes docker files asynchronously with Celery workers.

The full report can be found in `report.md.`

By Mustafa Al Quraishi

## Prerequisites

- Python 3.10+
- Redis
- Celery
- Docker
- Docker Compose (optional)

## Example Use

### Submitting

For sending a dockerfile job to be executed to the `/submit` endpoint:

```
curl --location 'http://127.0.0.1:5000/submit' \
--header 'Content-Type: application/octet-stream' \
--data '@/**/**/**/Dockerfile'
```

An example Dockerfile:

```
FROM ubuntu:latest
# train machine learning model
RUN mkdir -p /data
# save performances
CMD echo '{"perf":0.99}' > /data/perf.json
```

You can expect a response, if successful:

```
{"job_id": "41c25721-1410-4559-b5b2-50d98b3b5f00"}
```

### Checking Status

To check the current status of your job, to see if it has been successfully executed:

```
curl --location 'http://127.0.0.1:5000/status?job_id=41c25721-1410-4559-b5b2-50d98b3b5f00'
```

If processing the response will return:

```
{"status": "processing"}
```

If finished processing the response will return:

```
{"performance": 0.99, "status": "success"}
```

### Data Storage

Upon container execution, all data from jobs will be stored in `experiement_summaries` directory, each job will have its directory names after the `job_id`, with the following structure.

```
experiment_summaries
└── 41c25721-1410-4559-b5b2-50d98b3b5f00
 ├── Dockerfile
 └── data
   └── perf.json
```

### Check Celery Status

To check the health and status of tasks queued in the Celery worker:

Check the queued tasks:

```
curl --location 'http://127.0.0.1:5000/celery/tasks'
```

Check if the Celery worker is running:

```
curl --location 'http://127.0.0.1:5000/celery/ping'
```

## Getting Started (Local)

Set up a virtual environment and install dependencies with the `Makefile`:

```bash
make install
```

Make sure you are in the `ml-executor` virtual env:

```
conda activate ml-executor
```

Start the Redis server:

```bash
redis-server
```

If you do not have Redis installed:

```bash
run-redis.sh
```

In a new terminal window, start the Celery worker:

```bash
celery -A backend.index.celery_app worker --loglevel=info
```

Finally, start the Flask application:

```bash
python run.py
```

## Getting Started (Docker)

`Note:` Make sure you have Docker and Docker Compose installed. You do not need to install any dependencies, as they are already installed in the Docker container.

To run the application in a Docker container:

```bash
docker-compose up
```

Change the `app.config['BACKEND_TYPE']: BackendType = BackendType.LOCAL_SUBPROCESS` in `backend/config/server.py` to `BackendType.LOCAL_DOCKER` to run the application in a Docker container.

Define in your env file the following variables i.e. in your `~/.zshrc` or `~/.bashrc`:

```
 EXPORT HOST_SERVICE_DIRECTORY=/path/to/directory
```

## Update Environment

If you would like to update the conda env `ml-executor`:

```bash
make update
```

## Delete Environment

If you would like to delete the conda env `ml-executor`:

```bash
make clean
```
