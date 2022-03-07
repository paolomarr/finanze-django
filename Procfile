release: python $PWD/$BUILD_DIR/manage.py migrate
web: gunicorn --pythonpath $PWD/$BUILD_DIR finanze.wsgi
