# using a python small basic image
FROM python:3.10
# set environment variables
ENV DOCKER=true
ENV MONGODB_HOST=host.docker.internal
# exposing our app port in docker internal network
EXPOSE 11655
# creates a dir for our application
WORKDIR /app
# install build dependencies needed for packages with C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# copy our requirements.txt file and install dependencies
RUN pip install --upgrade pip setuptools wheel importlib-metadata
RUN python -c "import pkg_resources; pkg_resources.working_set" || true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# copy the rest of our application
COPY . /app
# run the application
# CMD gunicorn --statsd-host=localhost:9125 --statsd-prefix=helloworld --log-level=INFO --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11654 wsgi:app --reload
CMD gunicorn --log-level=WARNING --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11655 wsgi:app --reload
