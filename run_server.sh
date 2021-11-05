# clear
# cd api/
# echo "Loading..."
# # gunicorn routes:api --access-logfile - --reload  # live-reload (development only!)
# python app.py

clear
gunicorn --log-level=INFO --limit-request-line 0 -w 4 -k eventlet -b 0.0.0.0:11654 wsgi:app --reload
