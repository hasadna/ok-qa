web: python manage.py run_gunicorn -w 4 -b 0.0.0.0:$PORT
celery: python manage.py celery worker -E --maxtasksperchild=1000
