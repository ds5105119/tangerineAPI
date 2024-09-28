import asyncio
import json
import logging

from channels.layers import BaseChannelLayer
from confluent_kafka import KafkaError, KafkaException
from confluent_kafka.admin import NewTopic

from chats.models import *
from kafka.managers import KafkaManager

logger = logging.getLogger(__name__)


class KafkaChannelLayer(BaseChannelLayer):
    def __init__(self, prefix="channels", bootstrap_servers="localhost:9092", **kwargs):
        """
        kafka channel layer 초기화
        asyncio.lock에 의해 process별 kafka_manger가 고유함이 보장됩니다.
        """
        super().__init__(**kwargs)
        self.kafka_manager = KafkaManager(bootstrap_servers=bootstrap_servers)
        self.lock = asyncio.Lock()
        self.groups = {}
        self.prefix = prefix

    async def send(self, channel, message):
        """
        고유한 Kafka Producer를 사용하여 실행 중인 이벤트 루프에 채팅을 보내는 비동기 작업을 추가합니다.
        """
        async with self.lock:
            producer = await self.kafka_manager.get_producer()
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(
                None, lambda: producer.produce(channel, self.serialize(message), callback=self.delivery_report)
            )
            producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            raise

    async def receive(self, channel):
        async with self.lock:
            consumer = await self.kafka_manager.get_consumer(channel)
        while True:
            try:
                msg = await asyncio.get_event_loop().run_in_executor(None, consumer.poll, 1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    raise Exception(msg.error())
                return json.loads(msg.value().decode("utf-8"))
            except Exception as e:
                logger.error(f"Error receiving message from Kafka: {e}")
                raise

    async def group_add(self, group, channel):
        """유저를 특정 그룹(채팅방)에 추가"""
        assert self.valid_group_name(group), "Group name not valid"
        assert self.valid_channel_name(channel), "Channel name not valid"
        group_key = self._group_key(group)
        connection = self.connection(self.consistent_hash(group))
        # Add to group sorted set with creation time as timestamp
        await connection.zadd(group_key, {channel: time.time()})
        # Set expiration to be group_expiry, since everything in
        # it at this point is guaranteed to expire before that
        await connection.expire(group_key, self.group_expiry)

    async def group_discard(self, group, channel):
        """유저를 특정 그룹(채팅방)에서 제거"""
        pass

    async def group_send(self, group, message):
        """그룹(채팅방)에 속한 모든 유저에게 메시지 전달"""
        pass

    async def new_channel(self, prefix="specific"):
        channel = f"{prefix}.{uuid.uuid4().hex}"
        try:
            new_topic = NewTopic(channel, num_partitions=1, replication_factor=1)
            self.kafka_manager.admin_client.create_topics([new_topic])
        except KafkaException as e:
            logger.error(f"Failed to create new Kafka topic: {e}")
            raise
        return channel

    async def close(self):
        await self.kafka_manager.close()

    def _group_key(self, group):
        return f"{self.prefix}:group:{group}".encode()

    @staticmethod
    def serialize(message):
        """
        메시지 serializer 정적 메소드
        """
        return json.dumps(message).encode("utf-8")

    @staticmethod
    def delivery_report(err, msg):
        """
        로그 설정을 위한 정적 메소드
        """
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")
