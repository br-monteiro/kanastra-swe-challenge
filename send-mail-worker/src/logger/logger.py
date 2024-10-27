import logging
from src.config.settings import get_settings
from src.logger.formatter import Formatter

log_level = get_settings().log_level


def get_logger(name):
    logHandler = logging.StreamHandler()
    logHandler.setFormatter(Formatter())

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(logHandler)

    return logger
