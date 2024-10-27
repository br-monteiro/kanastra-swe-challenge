import pytest
from unittest.mock import MagicMock, patch
from src.services.send_mail_service import SendMailService


@pytest.fixture
def settings():
    return MagicMock()


@patch("src.services.send_mail_service.get_logger")
def test_init(get_logger, settings):
    service = SendMailService(settings)

    assert service.settings == settings
    get_logger.assert_called_once_with("src.services.send_mail_service")


@patch("src.services.send_mail_service.get_logger")
@patch("src.services.send_mail_service.METRICS")
def test_send_mail(metrics, get_logger, settings):
    service = SendMailService(settings)
    sqs_message = MagicMock(body="test")

    service.send_mail(sqs_message)

    metrics.get.assert_called_once_with("mails_sent")
    get_logger.return_value.debug.assert_called_once_with("Mail sent: test")
