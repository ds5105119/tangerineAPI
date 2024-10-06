import logging

from channels.db import database_sync_to_async
from channels.exceptions import AcceptConnection, DenyConnection, InvalidChannelLayerError
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


def get_handler_name(message):
    """
    Looks at a message, checks it has a sensible type, and returns the
    handler name for that type.
    """
    # Check message looks OK
    if "type" not in message:
        raise ValueError("Incoming message has no 'type' attribute")
    # Extract type and replace . with _
    handler_name = message["type"].replace(".", "_")
    if handler_name.startswith("_"):
        raise ValueError("Malformed type in message (leading underscore)")
    return handler_name


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, message):
        """
        Called when a WebSocket connection is opened.
        """
        try:
            for group in self.groups:
                await self.channel_layer.group_add(group, self.channel_name)
        except AttributeError:
            raise InvalidChannelLayerError("BACKEND is unconfigured or doesn't support groups")
        try:
            await self.connect()
        except AcceptConnection:
            await self.accept()
        except DenyConnection:
            await self.close()

    async def connect(self):
        logger.debug("WebSocket 연결 시도")
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user = self.scope["user"]

        logging.debug(
            f"일단 뭐냐 그룹에 추가는되었다 "
            f"{str(self.channel_layer.groups)}\n"
            f"{str(self.channel_layer.pulsar_manager.producers)}\n"
            f"{str(self.channel_layer.pulsar_manager.consumers)}\n"
            f"{str(self.channel_layer.pulsar_manager.channels)}\n"
            f"{str(self.room_id)}\n"
            f"{str(self.user)}\n"
        )

        if not self.user.is_authenticated:
            await self.close(code=401, reason="로그인을 진행해 주세요.")
            return None

        if not await self.check_room_exists(self.room_id):
            await self.close(code=403, reason="찾을 수 없습니다.")
            return None

        await self.channel_layer.group_add(self.room_id, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(
            self.room_id, {"type": "chat_message", "message": f"{self.user}님이 들어왔습니다."}
        )

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_id, self.channel_name)
        except Exception:
            pass

    async def websocket_receive(self, message):
        """
        Called when a WebSocket frame is received. Decodes it and passes it
        to receive().
        """
        logger.debug(f"웹소켓 메세지 수신: {message}")
        if "text" in message:
            await self.receive(text_data=message["text"])
        else:
            await self.receive(bytes_data=message["bytes"])

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        logger.debug(f"recieve 메세지 수신: {text_data}")
        if text_data:
            await self.receive_json(await self.decode_json(text_data), **kwargs)
        else:
            raise ValueError("No text section for incoming WebSocket frame!")

    async def receive_json(self, content, **kwargs):
        logger.debug(f"메세지 수신: {content}")
        message = content["message"]
        self.save_message(self.user, message)

        # room = await self.get_room_exists(self.room_id, self.user)

        await self.channel_layer.group_send(self.room_id, {"type": "chat_message", "message": message})

    async def chat_message(self, event):
        try:
            message = event["message"]
            await self.send_json({"message": message})
        except Exception:
            await self.send_json({"error": "메시지 전송 실패"})

    @database_sync_to_async
    def get_room_exists(self, room_id, user):
        return ChatRoom.objects.filter(uuid=room_id, chat_members_as_room__user=user).exists()

    @database_sync_to_async
    def save_message(self, user, message):
        ChatMessage.objects.create(member=user, message=message)

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return ChatRoom.objects.filter(uuid=room_id).exists()
