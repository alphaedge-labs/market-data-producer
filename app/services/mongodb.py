from motor.motor_asyncio import AsyncIOMotorClient
from settings.env import Settings
from utils.logging import logger
from datetime import datetime
from nanoid import generate

import pytz
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.timezone('UTC')

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Settings.MONGO_URI)
        self.db = self.client[Settings.MONGO_DB]
        self.collections = {
            "TICKS": "ticks",
            "MARKET_DATA": "market_data"
        }
    
    async def create_time_series_collection(self, collection_name):
        """Ensure the time-series collection exists."""
        try:
            # Check if collection exists first
            collections = await self.db.list_collection_names()
            if collection_name in collections:
                logger.info(f"Collection '{collection_name}' already exists")
                return
            
            await self.db.create_collection(
                collection_name,
                timeseries={
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "seconds"
                }
            )
            logger.info(f"Time-series collection '{collection_name}' created.")
        except Exception as e:
            logger.error(f"Error creating time-series collection '{collection_name}': {e}")

    async def async_store_timeseries_data_in_mongo(self, tick, metadata, collection_name, prefix):
        """Asynchronous MongoDB write."""
        # logger.info('Attempting to save tick data')
        
        try:
            tick_time = tick.get("ltt") or tick.get("time")
            if not tick_time:
                logger.error(f"No timestamp found in tick data: {tick}")
                return
            timestamp = datetime.strptime(tick_time, "%a %b %d %H:%M:%S %Y")
        except ValueError as e:
            logger.error(f"Invalid tick_time format: {tick_time}, error: {e}")
            return

        document = {
            "_id": prefix + generate("1234567890abcdef", 10),
            "timestamp": timestamp,
            "metadata": metadata,
            "data": tick,
        }

        try:
            await self.db[collection_name].insert_one(document)
            # logger.info(f"Data stored in collection '{collection_name}' successfully")
        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    async def update_user_token(self, broker_client_id, broker_name, access_token):
        """Update the user token in the database."""
        try:
            await self.db.users.update_one(
                {"is_admin": True},
                {"$set": {"streamer.STREAMER_SESSION_TOKEN": access_token, "updated_at": datetime.now(IST)}},
                upsert=True
            )
            logger.info(f"User token updated for {broker_name} client ID: {broker_client_id}")
        except Exception as e:
            logger.error(f"Error updating user token: {e}")

    async def get_streamer_credentials(self):
        try:
            admin_user = await self.db.users.find_one({"is_admin": True})
            streamer = admin_user.get("streamer", {})
            return streamer
        except Exception as e:
            logger.error(f"Error fetching streamer credentials: {e}")
            return {}

    async def close(self):
        """Close the database connection."""
        self.client.close()
        logger.info("Database connection closed.")

database = Database()