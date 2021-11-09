# using a python small basic image
FROM python:3.8
# set environment variables
ENV DOCKER=true
ENV MONGODB_HOST=host.docker.internal
# exposing our app port in docker internal network
EXPOSE 11654
# creates a dir for our application
WORKDIR /
# copy our requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
# copy the rest of our application
COPY . .
# run the application
# CMD gunicorn --statsd-host=localhost:9125 --statsd-prefix=helloworld --log-level=INFO --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11654 wsgi:app --reload
CMD gunicorn --log-level=INFO --limit-request-line 0 --workers 8 --worker-class eventlet  --bind 0.0.0.0:11654 wsgi:app --reload
