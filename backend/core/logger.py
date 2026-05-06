from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>",
           level="INFO")
