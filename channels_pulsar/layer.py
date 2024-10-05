import asyncio
import json
import logging
import time
import uuid

from channels.layers import BaseChannelLayer

from channels_pulsar.manager import PulsarChannelManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


class PulsarChannelLayer(BaseChannelLayer):
    def __init__(
        self,
        expiry=60,
        group_expiry=3600,
        capacity=100,
        channel_capacity=None,
        pulsar_client_url="pulsar://localhost:6650",
        admin_url="http://localhost:8080/admin/v2",
        topic_type="non-persistent",
        topic_tenant="public",
        topic_namespace="default",
        pulsar_ttl=10,
        **kwargs,
    ):
        super().__init__(
            expiry=expiry,
            capacity=capacity,
            channel_capacity=channel_capacity,
        )
        self.groups = {}
        self.group_expiry = group_expiry
        self.pulsar_manager = PulsarChannelManager(
            pulsar_client_url, admin_url, topic_type, topic_tenant, topic_namespace, pulsar_ttl
        )

    # Channel layer API

    extensions = ["groups", "flush"]

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

        producer = await self.pulsar_manager.get_producer(group)

        logger.debug(f"메지시 전송 시작, 프로듀서: {producer.topic()}")
        await producer.send(json.dumps(message))

    async def receive(self, channel):
        """
        channel에 도착한 메시지를 반환합니다.
        같은 채널에 코루틴이 두 개 이상 생성될 경우에, 안전을 보장하지 않습니다.
        """
        assert self.valid_channel_name(channel)
        await self._clean_expired()

        channels = self.pulsar_manager.channels.get(channel)
        if not channels:
            await self.pulsar_manager.close_channel(channel)

        consumer = None
        while not consumer:
            consumer = await self.pulsar_manager.get_consumer(channel)
            if consumer:
                break
            else:
                await asyncio.sleep(1)

        message = consumer.receive()
        message = json.loads(message.data())

        logging.debug(f"메시지 도착: {str(message)}")

        return message

    async def new_channel(self, prefix="specific"):
        """
        새로운 채널 이름(subscribe_name)을 반환합니다.
        "non-persistent://public/default/my-topic"
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
        for channel, groups in self.pulsar_manager.channels.items():
            if not groups:
                await self.pulsar_manager.close_channel(channel)

        # Group Expiration
        timeout = int(time.time()) - self.group_expiry
        for group in self.groups:
            for channel in list(self.groups.get(group, set())):
                if self.groups[group][channel] and int(self.groups[group][channel]) < timeout:
                    await self.pulsar_manager.close_group(group)

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

        await self.pulsar_manager.close_channel(channel)

    async def group_add(self, group, channel):
        """
        그룹에 새로운 멤버를 추가합니다.
        """
        assert self.valid_group_name(group), "Group name not valid"
        assert self.valid_channel_name(channel), "Channel name not valid"

        producer = await self.pulsar_manager.get_producer(group)
        consumer = await self.pulsar_manager.get_consumer(channel, group)

        logging.debug(f"그룹 add 이후 producer: {producer}" f"그룹 add 이후 consumer: {consumer}")

        self.groups.setdefault(group, {})
        self.groups[group][channel] = time.time()  # 그룹 채팅을 연 시간

    async def group_discard(self, group, channel):
        """
        그룹에서 멤버를 제거합니다.
        만약 그룹에 멤버가 없는 경우 그룹을 삭제합니다.
        """
        # Both should be text and valid
        assert self.valid_channel_name(channel), "Invalid channel name"
        assert self.valid_group_name(group), "Invalid group name"
        # Remove from group set

        if group in self.groups:
            if channel in self.groups[group]:
                await self.pulsar_manager.group_discard(channel, group)
                del self.groups[group][channel]
            if not self.groups[group]:
                await self.pulsar_manager.close_group(group)

    async def group_send(self, group, message):
        """
        그룹에 메시지를 보냅니다.
        """
        # Check types
        assert isinstance(message, dict), "Message is not a dict"
        assert self.valid_group_name(group), "Invalid group name"
        # Run clean
        await self._clean_expired()
        # Send to each channel
        try:
            await self.send(group, message)
        except Exception:
            pass
