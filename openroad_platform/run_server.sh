# clear
# cd api/
# echo "Loading..."
# # gunicorn routes:api --access-logfile - --reload  # live-reload (development only!)
# python app.py

clear
# Default to sync worker for compatibility across gunicorn builds.
gunicorn --log-level=DEBUG --limit-request-line 0 -w 4 -b 0.0.0.0:11654 wsgi:app --reload
# gunicorn --log-level=DEBUG --limit-request-line 0 -w 4 -b 0.0.0.0:11657 wsgi:app --reload
