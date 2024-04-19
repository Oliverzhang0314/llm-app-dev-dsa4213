# Accept Python version during build
ARG PYTHON_VERSION="3.11"

FROM python:${PYTHON_VERSION}-slim

# Install OS dependencies
RUN apt-get update && apt-get -y upgrade \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl build-essential

# Copy the current directory contents into the container at /usr/src/app
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]