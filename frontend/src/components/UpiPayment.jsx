import React, { useEffect, useState, useCallback } from "react";
import { QRCodeSVG } from "qrcode.react";
import { BookingApi } from "../api/api";

/**
 * props:
 *  bookingId, upiUri, amount, paymentWindowSeconds
 *  onConfirmed(bookingId) -> called after mock confirm succeeds
 *  onExpired() -> called when timer hits zero
 */
export default function UpiPayment({ bookingId, upiUri, amount, paymentWindowSeconds, onConfirmed, onExpired }) {
  const [secondsLeft, setSecondsLeft] = useState(paymentWindowSeconds);
  const [status, setStatus] = useState("waiting"); // waiting | confirming | confirmed | expired | failed

  useEffect(() => {
    if (status !== "waiting") return undefined;

    if (secondsLeft <= 0) {
      setStatus("expired");
      onExpired?.();
      return undefined;
    }

    const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [secondsLeft, status, onExpired]);

  const minutes = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const seconds = String(secondsLeft % 60).padStart(2, "0");
  const urgency = secondsLeft <= 30 ? "critical" : secondsLeft <= 60 ? "warning" : "normal";

  const handleMockConfirm = useCallback(async () => {
    setStatus("confirming");
    try {
      const txnRef = `MOCKTXN${Date.now()}`;
      await BookingApi.confirmPayment(bookingId, txnRef);
      setStatus("confirmed");
      onConfirmed?.(bookingId);
    } catch (err) {
      setStatus("failed");
    }
  }, [bookingId, onConfirmed]);

  return (
    <div className="upi-payment">
      <h3 className="section-title">Scan &amp; pay with any UPI app</h3>

      {status === "waiting" || status === "confirming" ? (
        <>
          <div className={`countdown countdown--${urgency}`}>
            <span className="countdown__label">Time remaining</span>
            <span className="countdown__clock">{minutes}:{seconds}</span>
          </div>

          <div className="qr-frame">
            <QRCodeSVG value={upiUri} size={220} level="M" includeMargin />
          </div>

          <p className="upi-amount">Amount payable: <strong>₹{amount.toFixed(2)}</strong></p>
          <p className="hint-text upi-uri-text">{upiUri}</p>

          <button
            className="btn btn--primary btn--full"
            onClick={handleMockConfirm}
            disabled={status === "confirming"}
          >
            {status === "confirming" ? "Confirming payment…" : "I have paid (simulate confirmation)"}
          </button>
        </>
      ) : null}

      {status === "confirmed" && (
        <div className="status-banner status-banner--success">
          Payment confirmed! Your ticket is booked.
        </div>
      )}

      {status === "expired" && (
        <div className="status-banner status-banner--danger">
          Payment window expired. Please restart the booking to hold your seats again.
        </div>
      )}

      {status === "failed" && (
        <div className="status-banner status-banner--danger">
          We couldn't confirm the payment. Please try again.
        </div>
      )}
    </div>
  );
}
