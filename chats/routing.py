from django.urls import re_path

from chats.consumers import *

websocket_urlpatterns = [
    re_path(r"chats/t/(?P<room_id>[\w-]+)/$", ChatConsumer.as_asgi()),
]
