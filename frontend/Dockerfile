# Accept Python version during build
ARG PYTHON_VERSION="3.11"

FROM python:${PYTHON_VERSION}-slim

# Install OS dependencies
RUN apt-get update && apt-get -y upgrade \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl build-essential

# Install Wave
ARG WAVE_VERSION="1.1.2"

ENV WAVE_HOME="/home/app/wave"
RUN \
    mkdir -p "${WAVE_HOME}" && \
    curl -fsSL https://github.com/h2oai/wave/releases/download/v${WAVE_VERSION}/wave-${WAVE_VERSION}-linux-amd64.tar.gz | tar -C ${WAVE_HOME} -xzv 2>&1
ENV WAVE_PATH="${WAVE_HOME}/wave-${WAVE_VERSION}-linux-amd64"

# Copy the current directory contents into the container at /usr/src/app
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Set permissions for the Entrypoint script
RUN chmod +x docker-entrypoint.sh

ARG PYTHON_MODULE
ENV PYTHON_MODULE="dashboard.py"

ENTRYPOINT [ "./docker-entrypoint.sh" ]