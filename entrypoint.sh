#!/bin/bash
# this script is used to boot the Docker container

touch /logs/server.log
touch /logs/app.log

exec gunicorn main:app \
    --bind=0.0.0.0:80 \
    --log-level=info \
    --log-file=/logs/server.log \
    --access-logfile=/logs/app.log
