# clear
# cd api/
# echo "Loading..."
# # gunicorn routes:api --access-logfile - --reload  # live-reload (development only!)
# python app.py

clear
gunicorn --log-level=DEBUG --limit-request-line 0 -w 16 -k eventlet -b 127.0.0.1:11654 wsgi:app --reload
