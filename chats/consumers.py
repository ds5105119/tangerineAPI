import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=401, reason="로그인을 진행해 주세요.")
            return None

        self.member = await self.get_member(self.room_id, self.user)
        if not self.member:
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

    async def receive_json(self, content, **kwargs):
        message = content["message"]
        await self.save_message(message)
        await self.channel_layer.group_send(self.room_id, {"type": "chat_message", "message": message})

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
    def save_message(self, message):
        ChatMessage.objects.create(member=self.member, text=message)
        ChatRoom.objects.filter(uuid=self.room_id).update(updated_at=timezone.now())
        ChatMember.objects.filter(id=self.member.id).update(updated_at=timezone.now())
