import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import *


class ChatConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def check_room_exists(self, room_id):
        # 주어진 ID로 채팅방이 존재하는지 확인합니다.
        return ChatRoom.objects.filter(id=room_id).exists()

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        # group_name = self.get_group_name(self.room_id)
        await self.accept()

    async def receive_json(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Kafka로 메시지를 보내기 (토픽 이름: room_group_name)
        # ApiConfig.producer.produce(self.room_group_name, value=json.dumps({"message": message}))
        # 메시지 전송 완료를 보장하기 위해 flush 호출
        # ApiConfig.producer.flush()
        # WebSocket으로 메시지 전송
        await self.send(text_data=json.dumps({"message": message}))

    async def disconnect(self, code):
        """
        Called when a WebSocket connection is closed.
        """
        pass

    @staticmethod
    def get_group_name(room_id):
        # 방 ID를 사용하여 고유한 그룹 이름을 구성합니다.
        return f"chat_room_{room_id}"
