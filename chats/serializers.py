from accounts.serializers import *
from chats.models import *

try:
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from django.db.models import Prefetch
    from rest_framework import serializers
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


User = get_user_model()


class WriteableChatRoomSelfSerializer(serializers.Serializer):
    handles = serializers.ListField(child=serializers.CharField(), write_only=True)
    members = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ["uuid", "owner", "created_at", "handles", "members"]
        read_only_fields = ["uuid", "owner", "created_at", "members"]

    def get_members(self, obj):
        return list(obj.chatmember_set.values_list("user__handle", flat=True))

    @transaction.atomic
    def create(self, validated_data):
        handles = validated_data.pop("handles")
        current_user = self.context["request"].user

        chat_room = ChatRoom.objects.create(owner=current_user)

        users = User.objects.filter(handle__in=handles)
        chat_members = [ChatMember(room=chat_room, user=user) for user in users]
        ChatMember.objects.bulk_create(chat_members)

        return chat_room

    @transaction.atomic
    def update(self, instance, validated_data):
        handles = validated_data.pop("handles")
        existing_members = instance.chatmember_set.values_list("user__handle", flat=True)

        to_add = handles - existing_members
        to_remove = existing_members - handles

        if to_add:
            users = User.objects.filter(handle__in=to_add)
            chat_members = [ChatMember(room=instance, user=user) for user in users]
            ChatMember.objects.bulk_create(chat_members)

        if to_remove:
            ChatMember.objects.filter(room=instance, user__handle__in=to_remove).delete()

        return instance

    @classmethod
    def setup_eager_loading(cls, queryset):
        return queryset.prefetch_related(
            Prefetch(
                "chatmember_set",
                queryset=ChatMember.objects.select_related("user", "user__profile").only(
                    "user__handle",
                ),
            )
        )
