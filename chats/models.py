import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False, blank=True, default="")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "chat_room"
        ordering = ["-updated_at"]


class ChatMember(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="chat_members_as_room")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_members_as_user")
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "chat_member"
        ordering = ["-updated_at"]
        constraints = [models.UniqueConstraint(fields=["room", "user"], name="unique_chatroom")]
        indexes = [
            models.Index(fields=["room"]),
            models.Index(fields=["user"]),
            models.Index(fields=["room", "user"]),
        ]


class ChatMessage(models.Model):
    member = models.ForeignKey(ChatMember, on_delete=models.SET_NULL, null=True, related_name="chat_messages_as_member")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_message"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]


class ChatCursor(models.Model):
    member = models.ForeignKey(ChatMember, on_delete=models.CASCADE, related_name="chat_cursors_as_member")
    timestamp = models.DateTimeField()
