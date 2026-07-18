"""
Email utility for sending booking confirmations and notifications.
Uses Azure Communication Services Email (replaces raw SMTP, which Gmail
blocks from Azure-hosted senders regardless of credential correctness).
"""

import logging
from typing import Optional

from azure.communication.email import EmailClient

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: Optional[str] = None,
    attachment: Optional[bytes] = None,
    attachment_name: Optional[str] = None,
) -> bool:
    """
    Send an email using Azure Communication Services.
    Falls back to logging in development mode.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        plain_body: Plain text fallback
        attachment: Optional file attachment bytes
        attachment_name: Attachment filename

    Returns:
        True if sent successfully, False otherwise
    """
    if settings.ENVIRONMENT == "development":
        logger.info(f"[DEV EMAIL] To: {to_email}, Subject: {subject}")
        logger.info(f"[DEV EMAIL] Body preview: {html_body[:200]}...")
        return True

    if not settings.ACS_CONNECTION_STRING:
        logger.error("ACS_CONNECTION_STRING not configured - cannot send email")
        return False

    try:
        client = EmailClient.from_connection_string(settings.ACS_CONNECTION_STRING)

        message = {
            "senderAddress": settings.FROM_EMAIL,
            "recipients": {
                "to": [{"address": to_email}]
            },
            "content": {
                "subject": subject,
                "html": html_body,
            },
        }
        if plain_body:
            message["content"]["plainText"] = plain_body

        # Note: attachments use a different shape in ACS (base64 content +
        # contentType) - not wired up here since the current app doesn't
        # send any; add if needed later.

        poller = client.begin_send(message)
        result = poller.result()

        logger.info(f"Email sent to {to_email}: {subject} (status: {result['status']})")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_booking_confirmation(booking_id: str, to_email: str, passenger_name: str,
                              route: str, date: str, departure: str, seats: str) -> bool:
    """Send booking confirmation email."""
    subject = f"SkyBus Booking Confirmed - {booking_id}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">SkyBus</h1>
            <p style="color: rgba(255,255,255,0.9); margin-top: 5px;">Booking Confirmed!</p>
        </div>
        <div style="padding: 30px; background: #f9fafb;">
            <h2 style="color: #1f2937;">Hi {passenger_name},</h2>
            <p>Your booking has been confirmed. Here are your trip details:</p>
            <div style="background: white; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #e5e7eb;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td style="padding: 8px 0; color: #6b7280;">Booking ID</td><td style="padding: 8px 0; font-weight: bold;">{booking_id}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Route</td><td style="padding: 8px 0;">{route}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Date</td><td style="padding: 8px 0;">{date}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Departure</td><td style="padding: 8px 0;">{departure}</td></tr>
                    <tr><td style="padding: 8px 0; color: #6b7280;">Seat(s)</td><td style="padding: 8px 0;">{seats}</td></tr>
                </table>
            </div>
            <p style="color: #6b7280; font-size: 14px;">Please arrive at the boarding point 15 minutes before departure.</p>
            <p style="color: #6b7280; font-size: 14px;">Show your booking ID or e-ticket at the time of boarding.</p>
        </div>
        <div style="padding: 20px; text-align: center; color: #9ca3af; font-size: 12px;">
            <p>SkyBus Technologies Pvt. Ltd.</p>
            <p>For support: support@skybus.in | 1800-123-SKYBUS</p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_body)


def send_cancellation_email(booking_id: str, to_email: str, passenger_name: str,
                            refund_amount: float) -> bool:
    """Send booking cancellation email."""
    subject = f"SkyBus Booking Cancelled - {booking_id}"
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #ef4444; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">SkyBus</h1>
            <p style="color: rgba(255,255,255,0.9); margin-top: 5px;">Booking Cancelled</p>
        </div>
        <div style="padding: 30px; background: #f9fafb;">
            <h2 style="color: #1f2937;">Hi {passenger_name},</h2>
            <p>Your booking <strong>{booking_id}</strong> has been cancelled.</p>
            <p>Refund of <strong>Rs.{refund_amount:.2f}</strong> will be credited to your account within 5-7 business days.</p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_body)
