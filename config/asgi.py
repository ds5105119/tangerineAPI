import os

from django.core.asgi import get_asgi_application
from django.urls import path

from kafka.auth import AuthMiddlewareStack
from kafka.routing import ProtocolTypeRouter, URLRouter
from kafka.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogAPI.settings.prod")
django_asgi_app = get_asgi_application()

from chats.consumers import ChatConsumer

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        path("chat/", ChatConsumer.as_asgi()),
                    ]
                )
            )
        ),
    }
)
