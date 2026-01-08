import logging

logger = logging.getLogger(__name__)


def send_notification(user_id, subject, message):
    """Simple notification stub that logs a message."""
    logger.info("Notify %s: %s - %s", user_id, subject, message)
    # In future, integrate with email or push services
