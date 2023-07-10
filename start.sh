#!/bin/sh

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn docker-service.wsgi:application \
    --bind unix:/tmp/gunicorn.sock \
    --workers 3 \
    --daemon

# Start Nginx processes
echo Starting Nginx.
exec nginx -g "daemon off;"
