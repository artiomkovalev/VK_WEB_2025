import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
chdir = BASE_DIR
pythonpath = BASE_DIR
bind = '127.0.0.1:8000'
workers = 2
command = os.path.join(BASE_DIR, 'venv/bin/gunicorn')
