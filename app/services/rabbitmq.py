import aio_pika
import json
from typing import Optional

class RabbitMQService:
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

    async def connect(self, url: str = "amqp://guest:guest@localhost/"):
        self.connection = await aio_pika.connect_robust(url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "market_data_exchange",
            type=aio_pika.ExchangeType.TOPIC
        )

        # Declare queues
        await self.channel.declare_queue("index_ticks_queue", durable=True)
        await self.channel.declare_queue("option_ticks_queue", durable=True)
        await self.channel.declare_queue("market_depth_queue", durable=True)

        # Bind queues to exchange
        await self.channel.queue_bind(
            "index_ticks_queue",
            "market_data_exchange",
            routing_key="market.ticks.index"
        )
        await self.channel.queue_bind(
            "option_ticks_queue",
            "market_data_exchange",
            routing_key="market.ticks.option"
        )
        await self.channel.queue_bind(
            "market_depth_queue",
            "market_data_exchange",
            routing_key="market.depth"
        )

    async def publish_message(self, routing_key: str, message: dict):
        if self.exchange:
            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=routing_key
            )

    async def close(self):
        if self.connection:
            await self.connection.close()
