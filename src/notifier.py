import asyncio
import logging
from enum import Enum
from typing import Any, Dict, Optional

import httpx
import pendulum

from src.settings import config

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "ℹ️"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "🚨"
    SUCCESS = "✅"


def create_slack_message(
    level: AlertLevel,
    title: str,
    message: str,
    details: Optional[Dict[str, Any]],
    error: Optional[Exception] = None,
) -> str:
    timestamp = pendulum.now("UTC").format("YYYY-MM-DD HH:mm:ss z")

    formatted_message = [
        f"{level.value} *{level.name}*",
        f"*{title}*",
        f"*Timestamp:* {timestamp}",
        f"*Message:* {message}",
    ]

    if details:
        detail_lines = []
        for key, value in details.items():
            detail_lines.append(f"\n• *{key}:* {value}")
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


async def send_slack_message(
    level: AlertLevel,
    title: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[Exception] = None,
):
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    formatted_message = create_slack_message(level, title, message, details, error)

    if not config.SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL is not set")

    async with httpx.AsyncClient(timeout=10.0) as client:
        for retry in range(MAX_RETRIES):
            try:
                response = await client.post(
                    config.SLACK_WEBHOOK_URL, json={"text": formatted_message}
                )
                if response.status_code == 200:
                    return
                else:
                    raise Exception(
                        f"Failed to send message: {response.status_code}, body={response.text}"
                    )
            except Exception as e:
                logger.error(
                    f"Failed to send Slack message (attempt {retry + 1}/{MAX_RETRIES}): {e}"
                )
                if retry < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * 2**retry)

    logger.critical(
        f"Failed to send Slack message after {MAX_RETRIES} attempts: {formatted_message}"
    )
