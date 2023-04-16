import logging
import os
import sys


def get_logger():
    """Returns logger object with sensible defaults for logging to stdout."""
    logger = logging.getLogger(__name__)
    logger.setLevel(os.environ["LOG_LEVEL"])
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    return logger
