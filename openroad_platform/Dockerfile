# using a python small basic image
FROM python:3.12-slim
# set environment variables
ENV DOCKER=true
# Set MONGODB_HOST with a default value, allowing it to be overridden at runtime
ENV MONGODB_HOST=${MONGODB_HOST:-host.docker.internal}
# exposing our app port in docker internal network
EXPOSE 11654
WORKDIR /app
# WORKDIR /
# copy our requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
# COPY . .
# run the application
# CMD gunicorn --statsd-host=localhost:9125 --statsd-prefix=helloworld --log-level=INFO --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11654 wsgi:app --reload
CMD gunicorn --log-level=WARNING --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11654 wsgi:app --reload
