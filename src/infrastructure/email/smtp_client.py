import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config.settings import Settings


class SmtpEmailSender:

    def __init__(self, settings: Settings):
        self.settings = settings

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> None:
        message = MIMEMultipart()
        message["From"] = self.settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(
            self.settings.SMTP_HOST, self.settings.SMTP_PORT
        ) as server:
            server.starttls()
            server.login(self.settings.SMTP_USER, self.settings.SMTP_PASSWORD)
            server.send_message(message)

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
        self, customer_email: str, service_order_id: str
    ) -> None:
        subject = "Service Order Approval Required"
        body = f"""
Your service order requires approval to proceed.

Service Order ID: {service_order_id}

Please review the details and approve or reject the service order.
        """
        await self.send_email(customer_email, subject, body)
