import asyncio
import json
import time
import uuid

from channels.layers import BaseChannelLayer

from channels_pulsar2.manager import PulsarChannelManager


class PulsarChannelLayer(BaseChannelLayer):
    def __init__(
        self,
        expiry=60,
        group_expiry=3600,
        capacity=300,
        channel_capacity=None,
        pulsar_client_url="pulsar://localhost:6650",
        admin_url="http://localhost:8080/admin/v2",
        topic_type="non-persistent",
        topic_tenant="public",
        topic_namespace="default",
        pulsar_ttl=10,
    ):
        super().__init__(
            expiry=expiry,
            capacity=capacity,
            channel_capacity=channel_capacity,
        )
        self.groups = {}
        self.group_expiry = group_expiry
        self.topic_type = topic_type
        self.pulsar_manager = PulsarChannelManager(
            pulsar_client_url, admin_url, topic_type, topic_tenant, topic_namespace, pulsar_ttl
        )

    # Channel layer API

    extensions = ["flush"]

    async def connect(self, groups, channel):
        assert self.valid_channel_name(channel), "Channel name not valid"

        topics = set(map(self.pulsar_manager.group_to_topic, groups))
        await self.pulsar_manager.update_consumer(channel, topics)

    async def send(self, group, message):
        """
        특정 그룹에 메시지를 보냅니다.
        """
        # Typecheck
        assert isinstance(message, dict), "message is not a dict"
        assert self.valid_group_name(group), "Group name not valid"
        # If it's a process-local channel, strip off local part and stick full
        # name in message
        assert "__asgi_channel__" not in message
        await self._clean_expired()

        producer = await self.pulsar_manager.get_producer(group)
        producer.send(json.dumps(message))

    async def receive(self, channel):
        """
        channel에 도착한 메시지를 반환합니다.
        """
        assert self.valid_channel_name(channel)
        await self._clean_expired()

        channels = self.pulsar_manager.channels.get(channel)
        if not channels:
            await self.pulsar_manager.consumer_close(channel)

        consumer = None
        while not consumer:
            consumer = await self.pulsar_manager.get_consumer(channel)
            if consumer:
                break
            else:
                await asyncio.sleep(1)

        message = await asyncio.to_thread(consumer.receive)
        if self.topic_type == "persistent":
            consumer.acknowledge(message)

        message = json.loads(message.data())

        return message

    async def close_channel(self, channel):
        await self.pulsar_manager.consumer_close(channel)

    async def new_channel(self, prefix="specific"):
        """
        새로운 채널 이름(subscribe_name)을 반환합니다.
        pulsar를 사용하여, !부분이 필요 없습니다. 클러스터 확장도 지원합니다.
        """
        return f"{prefix}{uuid.uuid4().hex}"

    # Expire cleanup

    async def _clean_expired(self):
        """
        만료된 그룹과 채널을 제거합니다
        만료된 메시지가 있는 그룹을 모두 삭제할 것 입니다.
        """
        # Channel cleanup
        channels = list(self.pulsar_manager.channels.items()).copy()
        for channel, groups in channels:
            if not groups:
                await self.pulsar_manager.consumer_close(channel)

        # Group Expiration
        timeout = int(time.time()) - self.group_expiry
        for group in self.groups:
            for channel in self.groups.get(group, set()):
                if self.groups[group][channel] and int(self.groups[group][channel]) < timeout:
                    await self.pulsar_manager.producer_delete(group)

    # Flush extension

    async def flush(self):
        await self.pulsar_manager.flush()

    # Groups extension
    async def _remove_from_groups(self, channel):
        """
        Removes a channel from all groups. Used when a message on it expires.
        """
        for channels in self.groups.values():
            if channel in channels:
                del channels[channel]

        await self.pulsar_manager.consumer_close(channel)
