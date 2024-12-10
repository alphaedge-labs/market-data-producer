from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PORT = int(os.getenv('PORT', 8005))
    DEBUG = os.getenv('DEBUG', False)

    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB = os.getenv('MONGO_DB')

    RABBITMQ_USER = os.getenv('RABBITMQ_USER')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')