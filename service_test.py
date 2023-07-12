import pytest
from flask import json
from flask_testing import TestCase
from unittest.mock import patch

from backend.index import app as flask_app

UUID = '123e4567-e89b-12d3-a456-426614174000'


class TestApp(TestCase):
    def create_app(self):
        app = flask_app
        app.config['TESTING'] = True
        return app

    # Test the /submit endpoint
    # -------------------------

    @patch('backend.index.submit_dockerfile')
    def test_submit_endpoint(self, mock_submit_dockerfile):
        dockerfile_content = """
        FROM ghcr.io/substra/substra-tools:0.20.0-nvidiacuda11.8.0-base-ubuntu22.04-python3.10

        # install dependencies
        RUN python3.10 -m pip install -U pip

        # Install substrafl, substra (and substratools if editable mode)


        # PyPi dependencies
        RUN python3.10 -m pip install --no-cache-dir torch==1.11.0

        # Install local dependencies


        ENTRYPOINT ["python3.10", "function.py", "--function-name", "train"]

        COPY . .
        """
        mock_submit_dockerfile.return_value = UUID

        response = self.client.post('/submit', data=dockerfile_content)

        # Assert the request got a successful response
        self.assert200(response)

        # Assert the job_id is in the response data
        data = json.loads(response.data)
        assert 'job_id' in data
        assert UUID == data['job_id']

    def test_submit_endpoint_no_dockerfile(self):
        response = self.client.post('/submit')

        # Assert the request got a unsuccessful response
        self.assert400(response)

        # Assert the error is in the response data
        data = json.loads(response.data)
        assert 'error' in data

    def test_submit_endpoint_invalid_dockerfile(self):
        dockerfile_content = """
        FROM ubuntu:latest
        USER root
        # train machine learning model
        RUN mkdir -p /data
        # save performances
        CMD echo '{"perf":0.99}' > /data/perf.json
        """

        response = self.client.post('/submit', data=dockerfile_content)

        # Assert the request got a unsuccessful response
        self.assert400(response)

        # Assert the error is in the response data
        data = json.loads(response.data)
        assert 'error' in data

    # Test the /status endpoint
    # -------------------------

    @patch('backend.index.get_job_status')
    def test_status_endpoint(self, mock_get_job_status):

        job_data = json.dumps({'job_status': 'processing'}).encode('utf-8')
        mock_get_job_status.return_value = job_data

        job_id = UUID
        response = self.client.get(f'/status?job_id={job_id}')
        mock_get_job_status.assert_called_with(job_id)

        # Assert the request got a successful response
        self.assert200(response)

        # Assert the job data is in the response
        data = json.loads(response.data)
        assert 'job_status' in data


# run the tests
if __name__ == "__main__":
    pytest.main()
