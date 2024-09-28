import asyncio
import logging
import os
from threading import Lock

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient

logger = logging.getLogger(__name__)


class KafkaManager:
    _instance = None
    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance.__init__(*args, **kwargs)
        return cls._instance

    def __init__(self, bootstrap_servers="localhost:9092"):
        if not hasattr(self, "initialized"):
            self.producer_config = {
                "bootstrap.servers": bootstrap_servers,
                "client.id": f"channels_layer_{os.getpid()}",
                "acks": "all",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
            self.consumer_config = {
                "bootstrap.servers": bootstrap_servers,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
            self.producer = None
            self.consumers = {}
            self.admin_client = None
            self.initialized = True
            self._producer_lock = asyncio.Lock()
            self._consumer_lock = asyncio.Lock()

    async def get_producer(self):
        async with self._producer_lock:
            if self.producer is None:
                try:
                    self.producer = Producer(self.producer_config)
                    logger.info("Kafka producer created successfully.")
                except KafkaException as e:
                    logger.error(f"Failed to create Kafka producer: {e}")
                    raise
            return self.producer

    async def get_consumer(self, channel):
        async with self._consumer_lock:
            if channel not in self.consumers:
                try:
                    config = self.consumer_config.copy()
                    config["group.id"] = f"channels_consumer_{channel}_{os.getpid()}"
                    consumer = Consumer(config)
                    consumer.subscribe([channel])
                    self.consumers[channel] = consumer
                    logger.info(f"Kafka consumer for channel {channel} created successfully.")
                except KafkaException as e:
                    logger.error(f"Failed to create Kafka consumer for channel {channel}: {e}")
                    raise
            return self.consumers[channel]

    async def get_admin_client(self):
        if self.admin_client is None:
            try:
                self.admin_client = AdminClient(self.kafka_config)
                logger.info("Kafka admin client created successfully.")
            except KafkaException as e:
                logger.error(f"Failed to create Kafka admin client: {e}")
                raise
        return self.admin_client

    async def close(self):
        if self.producer:
            logger.info("Flushing and closing Kafka producer.")
            await asyncio.get_event_loop().run_in_executor(None, self.producer.flush)
        for consumer in self.consumers.values():
            try:
                logger.info(f"Closing Kafka consumer for channel {consumer.subscription()}")
                consumer.close()
            except KafkaException as e:
                logger.error(f"Error while closing Kafka consumer: {e}")
