from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

WSGI_APPLICATION = "config.wsgi.prod.application.application"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

ADMIN_ENABLED = False

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CORS_ALLOW_CREDENTIALS = True

SOCIALACCOUNT_STORE_TOKENS = False