from __future__ import annotations

import time
from uuid import uuid4

import httpx
import pytest

from src.infrastructure.config.settings import Settings
from src.infrastructure.email.smtp_client import SmtpEmailSender


def _testmail_live_enabled(settings: Settings) -> bool:
    return bool(
        settings.TESTMAIL_ENABLED
        and settings.TESTMAIL_API_KEY
        and settings.TESTMAIL_NAMESPACE
    )


def _extract_email_list(payload: object) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("emails", "messages", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _message_text(message: dict) -> str:
    text_parts = []
    for key in ("text", "html", "body", "subject"):
        value = message.get(key)
        if isinstance(value, str):
            text_parts.append(value)
    return "\n".join(text_parts)


def _message_recipients(message: dict) -> str:
    recipient_fields = []
    for key in ("to", "deliveredTo", "destination"):
        value = message.get(key)
        if isinstance(value, str):
            recipient_fields.append(value)
        elif isinstance(value, list):
            recipient_fields.extend(str(item) for item in value)
    return " ".join(recipient_fields)


def _fetch_testmail_messages(settings: Settings, tag: str) -> list[dict]:
    params = {
        "apikey": settings.TESTMAIL_API_KEY,
        "namespace": settings.TESTMAIL_NAMESPACE,
        "tag": tag,
    }
    response = httpx.get(settings.TESTMAIL_API_BASE_URL, params=params, timeout=10.0)
    response.raise_for_status()
    return _extract_email_list(response.json())


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.testmail
async def test_smtp_sender_delivers_message_to_testmail_live():
    settings = Settings()
    if not _testmail_live_enabled(settings):
        pytest.skip(
            "Testmail live test requires TESTMAIL_ENABLED=true, TESTMAIL_API_KEY and TESTMAIL_NAMESPACE"
        )

    sender = SmtpEmailSender(settings)
    tag = f"smtp-{uuid4().hex}"
    recipient = f"{settings.TESTMAIL_NAMESPACE}.{tag}@inbox.testmail.app"
    subject = f"SMTP Integration {tag}"
    body = f"Body for {tag}"

    await sender.send_email(recipient, subject, body)

    deadline = time.monotonic() + 30
    messages = []
    while time.monotonic() < deadline:
        messages = _fetch_testmail_messages(settings, tag)
        if messages:
            break
        time.sleep(2)

    assert messages, "No email received from Testmail API before timeout"
    assert any(subject in _message_text(message) for message in messages)
    assert any(recipient in _message_recipients(message) for message in messages)
    assert any(body in _message_text(message) for message in messages)
