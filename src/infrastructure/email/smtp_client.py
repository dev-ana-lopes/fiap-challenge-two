import ssl
import smtplib
from asyncio import to_thread
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config.settings import Settings


class SmtpEmailSender:

    def __init__(self, settings: Settings):
        self.settings = settings

    def _smtp_auth_username(self) -> str:
        return self.settings.SMTP_USERNAME or self.settings.SMTP_USER

    def _from_email(self) -> str:
        return (
            self.settings.SMTP_FROM_EMAIL
            or self._smtp_auth_username()
            or "no-reply@localhost"
        )

    def _build_message(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> MIMEMultipart:
        smtp_auth_username = self._smtp_auth_username()
        if self.settings.SMTP_USE_AUTH and not smtp_auth_username:
            raise ValueError(
                "SMTP_USERNAME or SMTP_USER must be configured when SMTP_USE_AUTH is enabled"
            )
        if self.settings.SMTP_USE_AUTH and not self.settings.SMTP_PASSWORD:
            raise ValueError(
                "SMTP_PASSWORD must be configured when SMTP_USE_AUTH is enabled"
            )

        message = MIMEMultipart()
        message["From"] = self._from_email()
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))
        return message

    def _send_message(self, message: MIMEMultipart) -> None:
        smtp_auth_username = self._smtp_auth_username()
        with smtplib.SMTP(
            self.settings.SMTP_HOST,
            self.settings.SMTP_PORT,
            timeout=self.settings.SMTP_TIMEOUT,
        ) as server:
            server.ehlo()
            if self.settings.SMTP_USE_TLS:
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
            if self.settings.SMTP_USE_AUTH:
                server.login(smtp_auth_username, self.settings.SMTP_PASSWORD)
            server.send_message(message)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> None:
        message = self._build_message(to_email, subject, body)
        await to_thread(self._send_message, message)

    async def send_service_order_created(
        self, customer_email: str, service_order_id: str
    ) -> None:
        subject = "Service Order Created"
        body = f"""
Your service order has been created successfully.

Service Order ID: {service_order_id}
Status: RECEIVED

We will contact you soon with more details.
        """
        await self.send_email(customer_email, subject, body)

    async def send_status_changed(
        self, customer_email: str, service_order_id: str, new_status: str
    ) -> None:
        subject = "Service Order Status Updated"
        body = f"""
Your service order status has been updated.

Service Order ID: {service_order_id}
New Status: {new_status}

Please contact us if you have any questions.
        """
        await self.send_email(customer_email, subject, body)

    async def send_approval_request(
        self,
        customer_email: str,
        service_order_id: str,
        total: float | None = None,
    ) -> None:
        subject = "Service Order Approval Required"
        total_line = f"\nEstimated total: {total:.2f}\n" if total is not None else ""
        body = f"""
Your service order requires approval to proceed.

Service Order ID: {service_order_id}
{total_line}

Please review the details and approve or reject the service order.
        """
        await self.send_email(customer_email, subject, body)
