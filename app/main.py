# market_data_producer/main.py

import asyncio
from fastapi import FastAPI
import uvicorn
import pytz
from services.rabbitmq import RabbitMQService
from services.breeze import BreezeService

from settings.env import Settings

app = FastAPI()
IST = pytz.timezone("Asia/Kolkata")

class MarketDataProducer:
    def __init__(self):
        self.rabbitmq = RabbitMQService()
        self.breeze = BreezeService()

    async def _process_tick(self, tick):
        try:
            if tick.get("quotes") == "Quotes Data":
                if tick.get("symbol") in self.breeze.indexes:
                    await self.rabbitmq.publish_message(
                        "market.ticks.index",
                        {
                            "tick": tick,
                            "metadata": {"symbol": tick.get("symbol")}
                        }
                    )
                else:
                    await self.rabbitmq.publish_message(
                        "market.ticks.option",
                        {
                            "tick": tick,
                            "metadata": {
                                "symbol": tick.get("symbol"),
                                "product_type": tick.get("product_type"),
                                "expiry_date": tick.get("expiry_date"),
                                "strike_price": tick.get("strike_price"),
                                "right": tick.get("right")
                            }
                        }
                    )
            elif tick.get("quotes") == "Market Depth":
                await self.rabbitmq.publish_message(
                    "market.depth",
                    {
                        "tick": tick,
                        "metadata": {
                            "symbol": tick.get("symbol"),
                            "product_type": tick.get("product_type"),
                            "expiry_date": tick.get("expiry_date"),
                            "strike_price": tick.get("strike_price"),
                            "right": tick.get("right")
                        }
                    }
                )
        except Exception as e:
            print(f"Error processing tick: {e}")

    def on_ticks(self, tick):
        asyncio.create_task(self._process_tick(tick))

    async def start(self):
        # Connect to RabbitMQ
        await self.rabbitmq.connect(
            f"amqp://{Settings.RABBITMQ_USER}:{Settings.RABBITMQ_PASSWORD}@alphaedge__rabbitmq/"
        )
        
        # Initialize and connect Breeze
        await self.breeze.initialize()
        self.breeze.connect_websocket(self.on_ticks)
        self.breeze.subscribe_to_feeds()

    async def stop(self):
        self.breeze.disconnect()
        await self.rabbitmq.close()

producer = MarketDataProducer()

@app.on_event("startup")
async def startup_event():
    await producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await producer.stop()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=Settings.PORT)