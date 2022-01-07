#!/usr/bin/env bash
# example: ./flask-migrate.sh "create table"

export FLASK_APP=main.py
flask db migrate -m "$1"
