import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=401, reason="로그인을 진행해 주세요.")
            return None

        self.rooms = await self.get_rooms(self.user)

        await self.channel_layer.connect(self.rooms, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.close_channel(self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        message = content.get("message")
        room_id = message.get("room_id")
        member_id = message.get("member")
        text = message.get("text")

        logger.debug(message)

        if room_id and member_id:
            await self.save_message(text, room_id, member_id)
            await self.channel_layer.send(room_id, {"type": "chat_message", "message": message})
        else:
            await self.close(code=403, reason="room_id와 member_id가 제공되지 않았습니다.")

    async def chat_message(self, event):
        try:
            message = event["message"]
            await self.send_json({"message": message})
        except Exception:
            await self.send_json({"error": "메시지 전송 실패"})

    @database_sync_to_async
    def get_member(self, room, user):
        return ChatMember.objects.filter(room_id=room, user=user).first()

    @database_sync_to_async
    def get_rooms(self, user):
        return list(ChatMember.objects.filter(user=user).values_list("room", flat=True))

    @database_sync_to_async
    def save_message(self, message, room_id, member_id):
        ChatMessage.objects.create(member_id=member_id, text=message)
        ChatRoom.objects.filter(uuid=room_id).update(updated_at=timezone.now())
        ChatMember.objects.filter(id=member_id).update(updated_at=timezone.now())
