from accounts.serializers import *
from chats.models import *

try:
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from rest_framework import serializers
    from rest_framework.exceptions import ValidationError
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


User = get_user_model()


class ReadOnlyChatMemberSerializer(serializers.ModelSerializer):
    user = ReadOnlyUserExternalSerializer(read_only=True)

    class Meta:
        model = ChatMember
        fields = ["user"]
        read_only_fields = ["user"]


class ReadOnlyChatRoomSelfSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()
    members = ReadOnlyChatMemberSerializer(many=True, source="chat_members_as_room", read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["uuid", "owner", "created_at", "updated_at", "members"]
        read_only_fields = ["owner", "created_at", "updated_at", "members"]


class WriteableChatRoomSelfSerializer(serializers.ModelSerializer):
    handles = serializers.ListField(child=serializers.CharField(), write_only=True)
    members = ReadOnlyChatMemberSerializer(many=True, source="chat_members_as_room", read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["uuid", "owner", "created_at", "handles", "members"]
        read_only_fields = ["uuid", "owner", "created_at", "members"]

    @transaction.atomic
    def create(self, validated_data):
        handles = validated_data.pop("handles")
        current_user = self.context["request"].user
        handles.append(current_user.handle)
        users = User.objects.filter(handle__in=handles)

        if users.count() != len(handles):
            raise ValidationError("Unavailable handle is included")

        if users.count() == 2:
            chat_room = ChatRoom.objects.create()
        else:
            chat_room = ChatRoom.objects.create(owner=current_user)

        chat_members = [ChatMember(room=chat_room, user=user) for user in users]
        ChatMember.objects.bulk_create(chat_members)

        return chat_room

    @transaction.atomic
    def update(self, instance, validated_data):
        handles = set(validated_data.pop("handles"))
        existing_members = set(instance.chatmember_set.values_list("user__handle", flat=True))

        to_add = handles - existing_members
        to_remove = existing_members - handles

        if len(existing_members) == 2 and len(to_add) - len(to_remove) > 0:
            current_user = self.context["request"].user
            instance.owner = current_user
            instance.save()

        if to_add:
            users = User.objects.filter(handle__in=to_add)
            chat_members = [ChatMember(room=instance, user=user) for user in users]
            ChatMember.objects.bulk_create(chat_members)

        if to_remove:
            ChatMember.objects.filter(room=instance, user__handle__in=to_remove).delete()

        return instance


class ReadOnlyChatMessageSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["member", "text", "created_at"]
        read_only_fields = ["member", "text", "created_at"]
