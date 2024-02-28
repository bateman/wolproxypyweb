# Base image
FROM python:3.13-rc-slim-bookworm

# Label docker image
LABEL maintainer="Fabio Calefato <fabio.calefato@uniba.it>"
LABEL org.label-schema.license="MIT"

# Install dependencies
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get install curl build-essential libssl-dev libffi-dev python3-dev pkg-config -y --no-install-recommends \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set shell to /bin/bash -o pipefail
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Get Rust; NOTE: using sh for better compatibility with other base images
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
# Add .cargo/bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy
COPY wolproxypyweb wolproxypyweb
COPY config config
COPY .flaskenv .flaskenv
COPY main.py main.py
COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh \
    && mkdir -p logs \
    && mkdir -p db

# Export ports
EXPOSE 80

# Run start script
ENTRYPOINT ["./entrypoint.sh"]
