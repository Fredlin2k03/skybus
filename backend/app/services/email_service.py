"""
Booking confirmation email service.
Uses SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD / FROM_EMAIL
already defined in app/config.py — no new settings needed.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_booking_confirmation_email(
    to_email: str,
    passenger_name: str,
    booking_id: str,
    bus_operator: str,
    origin: str,
    destination: str,
    departure_time: str,
    seat_numbers: list[str],
    total_fare: float,
    payment_id: str,
) -> bool:
    """
    Sends a booking confirmation email.
    Returns True on success, False on failure — never raises,
    so a flaky SMTP send never breaks the booking flow itself.
    """
    subject = f"SkyBus Booking Confirmed — {booking_id}"

    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #222;">
        <h2>Your SkyBus ticket is confirmed!</h2>
        <p>Hi {passenger_name},</p>
        <p>Your booking <strong>{booking_id}</strong> is confirmed. Details below:</p>
        <table style="border-collapse: collapse; width: 100%; max-width: 480px;">
          <tr><td style="padding:6px 0;"><strong>Operator</strong></td><td>{bus_operator}</td></tr>
          <tr><td style="padding:6px 0;"><strong>Route</strong></td><td>{origin} → {destination}</td></tr>
          <tr><td style="padding:6px 0;"><strong>Departure</strong></td><td>{departure_time}</td></tr>
          <tr><td style="padding:6px 0;"><strong>Seat(s)</strong></td><td>{", ".join(seat_numbers)}</td></tr>
          <tr><td style="padding:6px 0;"><strong>Amount paid</strong></td><td>₹{total_fare:.2f}</td></tr>
          <tr><td style="padding:6px 0;"><strong>Payment ID</strong></td><td>{payment_id}</td></tr>
        </table>
        <p style="margin-top:20px;">Safe travels!<br/>— Team SkyBus</p>
      </body>
    </html>
    """

    text_body = (
        f"Your SkyBus ticket is confirmed!\n\n"
        f"Booking ID: {booking_id}\n"
        f"Operator: {bus_operator}\n"
        f"Route: {origin} -> {destination}\n"
        f"Departure: {departure_time}\n"
        f"Seat(s): {', '.join(seat_numbers)}\n"
        f"Amount paid: Rs.{total_fare:.2f}\n"
        f"Payment ID: {payment_id}\n\n"
        f"Safe travels! - Team SkyBus"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, [to_email], msg.as_string())
        logger.info(f"Booking confirmation email sent to {to_email} for {booking_id}")
        return True
    except Exception as e:
        # Log and swallow — a booking should still succeed even if email fails.
        # Consider a retry queue (e.g. a background task or Azure Queue Storage)
        # if guaranteed delivery matters for the demo.
        logger.error(f"Failed to send confirmation email for {booking_id}: {e}")
        return False
