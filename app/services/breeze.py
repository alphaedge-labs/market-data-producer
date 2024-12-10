from breeze_connect import BreezeConnect
from typing import Optional, List, Dict, Callable
from services.mongodb import database
from utils.logging import logger

class BreezeService:
    def __init__(self):
        self.client: Optional[BreezeConnect] = None
        self.indexes: List[str] = ['4.1!NIFTY 50']
        self.expiry_dates: Dict[str, None] = {"4.1!NIFTY 50": None}

    async def initialize(self):
        """Initialize the BreezeConnect client with credentials from the database."""
        try:
            # Fetch streamer credentials from the database
            streamer_credentials = await database.get_streamer_credentials()
            if not streamer_credentials:
                raise ValueError("Streamer credentials not found in the database.")

            # Extract required fields
            api_key = streamer_credentials.get("STREAMER_APP_KEY")
            api_secret = streamer_credentials.get("STREAMER_SECRET_KEY")
            session_token = streamer_credentials.get("STREAMER_SESSION_TOKEN")

            if not all([api_key, api_secret, session_token]):
                raise ValueError("Incomplete streamer credentials found.")

            # Initialize BreezeConnect
            self.client = BreezeConnect(api_key=api_key)
            self.client.generate_session(api_secret=api_secret, session_token=session_token)

            logger.info("BreezeConnect client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize BreezeConnect: {e}")
            self.client = None  # Ensure breeze is not partially initialized

    def connect_websocket(self, on_ticks_callback: Callable):
        if self.client:
            self.client.ws_connect()
            self.client.on_ticks = on_ticks_callback

    def subscribe_to_feeds(self):
        if self.client:
            for index in self.indexes:
                response = self.client.subscribe_feeds(stock_token=index)
                print(f"Subscribed to feed for {index}: {response}")

    def disconnect(self):
        if self.client:
            self.client.ws_disconnect()

breeze = BreezeService()