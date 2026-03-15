from __future__ import annotations

import pytest
from email import message_from_bytes
from email.policy import default

from src.infrastructure.config.settings import Settings
from src.infrastructure.email.smtp_client import SmtpEmailSender


class _FakeSmtp:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.ehlo_calls = 0
        self.starttls_called = False
        self.starttls_context = None
        self.login_called = False
        self.login_args = None
        self.sent_messages = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        self.ehlo_calls += 1

    def starttls(self, context=None):
        self.starttls_called = True
        self.starttls_context = context

    def login(self, user, password):
        self.login_called = True
        self.login_args = (user, password)

    def send_message(self, message):
        self.sent_messages.append(message)


def _build_settings(**overrides) -> Settings:
    base = {
        "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/db",
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": 587,
        "SMTP_USERNAME": "notifications@example.com",
        "SMTP_USER": "",
        "SMTP_PASSWORD": "secret",
        "SMTP_FROM_EMAIL": "billing@example.com",
        "SMTP_USE_TLS": True,
        "SMTP_USE_AUTH": True,
        "SMTP_TIMEOUT": 10,
        "JWT_SECRET": "test",
    }
    base.update(overrides)
    return Settings(**base)


def _install_fake_smtp(monkeypatch):
    created = {}

    def fake_smtp(host, port, timeout=None):
        created["client"] = _FakeSmtp(host, port, timeout=timeout)
        return created["client"]

    import src.infrastructure.email.smtp_client as smtp_client_module

    monkeypatch.setattr(smtp_client_module.smtplib, "SMTP", fake_smtp)
    return created


@pytest.mark.asyncio
async def test_smtp_sender_can_skip_tls_and_auth(monkeypatch):
    created = _install_fake_smtp(monkeypatch)
    settings = _build_settings(
        SMTP_HOST="mailhog",
        SMTP_PORT=1025,
        SMTP_USERNAME="",
        SMTP_FROM_EMAIL="",
        SMTP_USE_TLS=False,
        SMTP_USE_AUTH=False,
    )

    sender = SmtpEmailSender(settings)
    await sender.send_email("to@example.com", "Subject", "Body")

    client = created["client"]
    assert client.host == "mailhog"
    assert client.port == 1025
    assert client.timeout == 10
    assert client.ehlo_calls == 1
    assert client.starttls_called is False
    assert client.login_called is False
    assert len(client.sent_messages) == 1
    message = client.sent_messages[0]
    assert message["From"] == "no-reply@localhost"
    assert message["To"] == "to@example.com"
    assert message["Subject"] == "Subject"
    parsed = message_from_bytes(message.as_bytes(), policy=default)
    assert parsed.get_body(preferencelist=("plain",)).get_content_charset() == "utf-8"
    assert "Body" in parsed.get_body(preferencelist=("plain",)).get_content()


@pytest.mark.asyncio
async def test_smtp_sender_uses_tls_and_auth_when_enabled(monkeypatch):
    created = _install_fake_smtp(monkeypatch)
    settings = _build_settings()

    sender = SmtpEmailSender(settings)
    await sender.send_email("to@example.com", "Subject", "Body")

    client = created["client"]
    assert client.ehlo_calls == 2
    assert client.starttls_called is True
    assert client.starttls_context is not None
    assert client.login_called is True
    assert client.login_args == ("notifications@example.com", "secret")
    assert len(client.sent_messages) == 1
    assert client.sent_messages[0]["From"] == "billing@example.com"


@pytest.mark.asyncio
async def test_smtp_sender_uses_legacy_smtp_user_for_auth(monkeypatch):
    created = _install_fake_smtp(monkeypatch)
    settings = _build_settings(
        SMTP_USERNAME="",
        SMTP_USER="legacy-user@example.com",
        SMTP_FROM_EMAIL="",
    )

    sender = SmtpEmailSender(settings)
    await sender.send_email("to@example.com", "Subject", "Body")

    client = created["client"]
    assert client.login_called is True
    assert client.login_args == ("legacy-user@example.com", "secret")
    assert client.sent_messages[0]["From"] == "legacy-user@example.com"


@pytest.mark.asyncio
async def test_smtp_sender_requires_auth_username_when_auth_is_enabled():
    sender = SmtpEmailSender(
        _build_settings(SMTP_USERNAME="", SMTP_USER="", SMTP_FROM_EMAIL="")
    )

    with pytest.raises(
        ValueError,
        match="SMTP_USERNAME or SMTP_USER must be configured when SMTP_USE_AUTH is enabled",
    ):
        await sender.send_email("to@example.com", "Subject", "Body")


@pytest.mark.asyncio
async def test_smtp_sender_requires_password_when_auth_is_enabled():
    sender = SmtpEmailSender(_build_settings(SMTP_PASSWORD=""))

    with pytest.raises(
        ValueError,
        match="SMTP_PASSWORD must be configured when SMTP_USE_AUTH is enabled",
    ):
        await sender.send_email("to@example.com", "Subject", "Body")
