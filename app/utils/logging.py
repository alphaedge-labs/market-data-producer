from loguru import logger

logger.add("alphaedge__market_data_producer.log", rotation="10 MB", level="DEBUG", format="{time} {level} {message}", backtrace=True, diagnose=True)