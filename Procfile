release: python manage.py migrate
web: gunicorn --pythonpath $PWD/$BUILD_DIR finanze.wsgi
