import os

workers = 2
wsgi_app = "config.asgi:application"
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120
loglevel = "info"
accesslog = "-"
errorlog = "-"
max_requests = 50
max_requests_jitter = 50

if os.environ.get("DEBUG", None) == "True":
    loglevel = "debug"
    accesslog = "-"
    errorlog = "-"
    reload = True
