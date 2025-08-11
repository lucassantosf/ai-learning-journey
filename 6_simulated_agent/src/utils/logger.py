import logging
import os
import time
from functools import wraps

def setup_logger(name="agent_logger", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to prevent duplicate logging
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    os.makedirs("logs", exist_ok=True)
    file = logging.FileHandler("logs/agent.log")
    file.setFormatter(formatter)
    logger.addHandler(file)

    return logger

def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = setup_logger()
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper
