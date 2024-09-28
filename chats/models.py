import uuid

from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_room"


class ChatMember(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "chat_member"
        constraints = [models.UniqueConstraint(fields=["room", "user"], name="unique_chatroom")]


class ChatMessage(models.Model):
    member = models.ForeignKey(ChatMember, on_delete=models.CASCADE, related_name="member")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_message"


class ChatCursor(models.Model):
    member = models.ForeignKey(ChatMember, on_delete=models.CASCADE, related_name="cursor")
    timestamp = models.DateTimeField()
