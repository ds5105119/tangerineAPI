import asyncio
import logging

import pulsar
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


class PulsarChannelManager:
    """
    Singleton Class for Pulsar Consumers and Producers
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(
        self,
        pulsar_client_url: str = "pulsar://localhost:6650",
        admin_url: str = "http://localhost:8080/admin/v2",
        topic_type: str = "non-persistent",
        topic_tenant: str = "public",
        topic_namespace: str = "default",
        pulsar_ttl: int = 10,
        schema=pulsar.schema.StringSchema,
    ):
        """
        @param pulsar_client_url: pulsar broker advertisedListeners URL
        @param admin_url: admin broker advertisedListeners URL
        @param topic_type: persistent: save to bookkeeper, non-persistent: In-memory(fast)
        @param topic_tenant: topic tenant advertisedListeners URL
        @param topic_namespace: topic namespace advertisedListeners URL
        @param pulsar_ttl: pulsar message's ttl in namespace
        @param schema: pulsar schema at this time only supports StringSchema
        """
        if not hasattr(self, "initialized"):
            self.producers: dict[str, pulsar.Producer] = {}
            self.consumers: dict[str, pulsar.Consumer] = {}
            self.channels: dict[str, set[str]] = {}
            self._producer_lock = asyncio.Lock()
            self._consumer_lock = asyncio.Lock()
            self.client = pulsar.Client(pulsar_client_url)
            self.pulsar_client_url = pulsar_client_url
            self.admin_url = admin_url
            self.topic_type = topic_type
            self.topic_tenant = topic_tenant
            self.topic_namespace = topic_namespace
            self.schema = schema()
            self.pulsar_ttl = pulsar_ttl
            self.initialized = True

    def __del__(self):
        """
        channel manager 객체가 해제될 때 호출되는 메서드
        """
        self.client.shutdown()

    def init_pulsar(self):
        requests.post(
            (f"{self.admin_url}/namespaces" f"/{self.topic_tenant}" f"/{self.topic_namespace}/messageTTL"),
            json=self.pulsar_ttl,
        )

    def group_to_topic(self, group: str) -> str:
        """
        @param group: channels의 그룹 이름
        @return: pulsar의 토픽 이름
        """
        return f"{self.topic_type}://{self.topic_tenant}/{self.topic_namespace}/{group}"

    async def get_producer(self, group: str) -> pulsar.Producer:
        """
        Pulsar Producer의 channels 고수준 Wrapper
        @param group: 그룹의 이름
        @return: 그룹의 producer
        """
        topic = self.group_to_topic(group)

        if topic in self.producers:
            return self.producers[topic]

        async with self._producer_lock:
            self.producers[topic] = self.client.create_producer(topic, schema=self.schema)

        return self.producers[topic]

    async def get_consumer(self, channel: str) -> pulsar.Consumer | None:
        """
        Pulsar Consumer의 channels 고수준 Wrapper
        @param channel: 채널의 이름
        @param force_update: true인 경우 강제로 consumer가 업데이트 됩니다.
        @return: 채널에 해당하는 consumer가 없는 경우 새로운 컨슈머
        """
        self.channels.setdefault(channel, set())

        if channel not in self.consumers.keys():
            return None

        return self.consumers[channel]

    async def update_consumer(self, channel: str, topics: set[str]):
        """
        @param channel: 해당 consumer channel
        @param topics: 해당 consumer가 갖게 될 topics
        @return: None
        """
        await self.consumer_close(channel)
        self.channels[channel] = topics

        async with self._consumer_lock:
            try:
                self.consumers[channel] = await asyncio.to_thread(
                    self.client.subscribe,
                    topic=list(self.channels[channel]),
                    subscription_name=channel,
                    schema=self.schema,
                )
            except pulsar.PulsarException as e:
                raise e

    async def consumer_add(self, channel: str, group: str):
        """
        @param channel: 채널의 이름
        @param group: 구독을 추가할 그룹의 이름
        @return: 채널에 해당하는 consumer에서 group의 구독을 추가합니다.
        """
        topic = self.group_to_topic(group)
        self.channels[channel].add(topic)
        topics = self.channels[channel].copy()
        await self.update_consumer(channel, topics)

    async def consumer_remove(self, channel: str, group: str):
        """
        @param channel: 채널의 이름
        @param group: 구독을 해제할 그룹의 이름
        @return: 채널에 해당하는 consumer에서 group의 구독을 해지합니다.
        """
        topic = self.group_to_topic(group)
        if topic in self.channels[channel]:
            self.channels[channel].discard(topic)
        topics = self.channels[channel].copy()
        await self.update_consumer(channel, topics)

    async def consumer_close(self, channel: str):
        """
        DO NOT USE WITHOUT LOCK
        @param channel: 삭제할 채널
        @return: None
        """
        if channel in self.channels.keys():
            del self.channels[channel]

        if channel in self.consumers.keys():
            self.consumers[channel].unsubscribe()
            self.consumers[channel].close()
            del self.consumers[channel]

    async def producer_close(self, group: str):
        """
        그룹 종료
        @param group: 종료할 그룹의 이름
        @return: None
        """
        topic = self.group_to_topic(group)

        if topic in self.producers:
            self.producers[topic].close()
            del self.producers[topic]

        for channels in self.channels.values():
            channels.discard(topic)

    async def producer_delete(self, group: str):
        """
        프로듀서 삭제
        @param group: 삭제할 그룹의 이름
        @return: None
        """
        topic_url = (
            f"{self.admin_url}"
            f"/{self.topic_type}"
            f"/{self.topic_tenant}"
            f"/{self.topic_namespace}"
            f"/{group}?force=true"
        )
        requests.delete(topic_url)

    async def flush(self):
        self.client.close()
        self.producers = {}
        self.consumers = {}
        self.channels = {}
        self.client = pulsar.Client(self.pulsar_client_url)
