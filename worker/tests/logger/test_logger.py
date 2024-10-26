import logging
from src.config.settings import get_settings
from src.logger.logger import get_logger


def test_logger_creation():
    logger_name = "test_logger"
    expected_log_level = get_settings().log_level.upper()

    logger = get_logger(logger_name)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == getattr(logging, expected_log_level)


def test_log_message(caplog):
    logger = get_logger("test_logger")
    message = "Test log message"

    logger.info(message)

    assert len(caplog.records) == 1
    assert caplog.records[0].message == message


def test_log_format(caplog):
    logger = get_logger("test_logger")
    message = "Test log message"

    logger.info(message)

    assert len(caplog.records) == 1
    assert caplog.records[0].message == message
    assert caplog.records[0].name == "test_logger"
    assert 'INFO' == caplog.records[0].levelname
