#!/bin/bash
# this script is used to boot the Docker container

touch /logs/error.log
touch /logs/access.log

exec gunicorn main:app \
    --bind=0.0.0.0:80 \
    --log-level=info \
    --error-logfile=/logs/error.log \
    --access-logfile=/logs/info.log
