#!/bin/bash
# this script is used to boot the Docker container

mkdir -p /logs/gunicorn
touch /logs/gunicorn/error.log
touch /logs/gunicorn/access.log
chmod -R +r /logs/gunicorn

exec gunicorn main:app \
    --bind=0.0.0.0:80 \
    --log-level=info \
    --error-logfile=/logs/error.log \
    --access-logfile=/logs/info.log
