# src/logging_config.py
import logging

logger = logging.getLogger("nl2sql_logger")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(handler)
