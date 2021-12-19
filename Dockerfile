# Base image
FROM python:slim

# Label docker image
LABEL maintainer="Fabio Calefato <fabio.calefato@uniba.it>"
LABEL org.label-schema.license="MIT"

# Install dependencies
COPY Makefile Makefile
COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && make production \
    && apt-get purge -y --auto-remove gcc build-essential

# Copy
COPY wolproxypyweb wolproxypyweb
COPY config config
COPY .flaskenv .flaskenv
COPY main.py main.py
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

RUN mkdir -p logs
RUN mkdir -p db

# Export ports
EXPOSE 80

# Run start script
ENTRYPOINT ["./entrypoint.sh"]
