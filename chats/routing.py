from django.urls import re_path

from chats.consumers import *

websocket_urlpatterns = [
    re_path(r"chats/t", ChatConsumer.as_asgi()),
]
