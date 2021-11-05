# using a python small basic image
FROM python:3.8
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
CMD gunicorn --log-level=INFO --limit-request-line 0 -w 16 -k eventlet -b 0.0.0.0:11654 wsgi:app --reload

