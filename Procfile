web: . ENV/bin/activate; python manage.py run_gunicorn -w 4 -b 0.0.0.0:$PORT
celery: . ENV/bin/activate; python manage.py celery worker -E --maxtasksperchild=1000
