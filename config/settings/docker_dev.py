from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

ADMIN_ENABLED = True

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",  # 디버그 레벨로 설정
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "django.request": {
            "handlers": ["console"],
            "level": "DEBUG",  # 요청 관련 로그
            "propagate": True,
        },
        "allauth": {
            "handlers": ["console"],
            "level": "DEBUG",  # Allauth 관련 디버깅 정보
            "propagate": True,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "DEBUG",  # 보안 관련 로그
            "propagate": True,
        },
        "requests_oauthlib": {
            "handlers": ["console"],
            "level": "DEBUG",  # OAuth 인증 요청 및 응답 로그
            "propagate": True,
        },
    },
}


# Elasticsearch configuration

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": "https://127.0.0.1:9200",
        "basic_auth": (
            env("ELASTICSEARCH_DSL_USERNAME"),
            env("ELASTICSEARCH_DSL_PASSWORD"),
        ),
        "ca_certs": os.path.join(BASE_DIR, "elasticsearch_ca.crt"),
    }
}
