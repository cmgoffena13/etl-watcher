import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

import pendulum
from slack_sdk import WebhookClient

from src.settings import config

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "ℹ️"
    WARNING = "⚠️"
    ERROR = "❌"
    SUCCESS = "✅"


def create_slack_message(
    level: AlertLevel,
    message: str,
    details: Optional[Dict[str, Any]],
    error: Optional[Exception] = None,
) -> str:
    timestamp = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss z")

    formatted_message = [
        f"{level.value} *{level.name}*",
        f"*Timestamp:* {timestamp}",
        f"*Message:* {message}",
    ]

    if details:
        detail_lines = []
        for key, value in details.items():
            detail_lines.append(f"• *{key}:* {value}")
        if detail_lines:
            formatted_message.append("\n*Details:*")
            formatted_message.extend(detail_lines)

    if error:
        formatted_message.extend(
            [
                "\n*Error Details:*",
                f"• *Type:* {type(error).__name__}",
                f"• *Message:* {str(error)}",
            ]
        )

    return "\n".join(formatted_message)


def send_slack_message(
    level: AlertLevel,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
):
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    formatted_message = create_slack_message(level, message, details, error)

    webhook = WebhookClient(config.SLACK_WEBHOOK_URL)

    if not webhook:
        raise ValueError("SLACK_WEBHOOK_URL is not set")

    for retry in range(MAX_RETRIES):
        try:
            response = webhook.send(text=formatted_message)
            if response.status_code == 200:
                return
            else:
                raise Exception(
                    f"Failed to send message: {response.status_code}, body={response.body}"
                )
        except Exception as e:
            logger.error(
                f"Failed to send Slack message (attempt {retry + 1}/{MAX_RETRIES}): {e}"
            )
            if retry < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * 2**retry)

    logger.critical(
        f"Failed to send Slack message after {MAX_RETRIES} attempts: {formatted_message}"
    )
