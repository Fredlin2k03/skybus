"""
Email utility for sending booking confirmations and notifications.
Uses SMTP with fallback to console output in development.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
from typing import Optional

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
    Send an email using SMTP.
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
    
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"SkyBus <{settings.FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        
        if plain_body:
            msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
        
        if attachment and attachment_name:
            att = MIMEApplication(attachment)
            att.add_header("Content-Disposition", "attachment", filename=attachment_name)
            msg.attach(att)
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
        
        logger.info(f"Email sent to {to_email}: {subject}")
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
            <h1 style="color: white; margin: 0;">🚌 SkyBus</h1>
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
            <h1 style="color: white; margin: 0;">🚌 SkyBus</h1>
            <p style="color: rgba(255,255,255,0.9); margin-top: 5px;">Booking Cancelled</p>
        </div>
        <div style="padding: 30px; background: #f9fafb;">
            <h2 style="color: #1f2937;">Hi {passenger_name},</h2>
            <p>Your booking <strong>{booking_id}</strong> has been cancelled.</p>
            <p>Refund of <strong>₹{refund_amount:.2f}</strong> will be credited to your account within 5-7 business days.</p>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, subject, html_body)
