import os
import logging

from backend.index import app
from backend.config.server import EXPERIMENT_SUMMARIES


if __name__ == '__main__':

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("flask")

    # Create folder for Dockerfiles
    if not os.path.exists(f'./{EXPERIMENT_SUMMARIES}'):
        os.makedirs(f'./{EXPERIMENT_SUMMARIES}')

    # Run Flask app
    app.run(host='0.0.0.0', debug=True)
