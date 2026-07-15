import React from "react";

const CONVENIENCE_FEE_RATE = 0.02; // 2%, kept client-visible for transparency; server recomputes independently

export default function FareSummary({ seats, boardingPoint, droppingPoint, onProceed, isSubmitting }) {
  const seatTotal = seats.reduce((sum, s) => sum + s.price, 0);
  const convenienceFee = Math.round(seatTotal * CONVENIENCE_FEE_RATE * 100) / 100;
  const total = seatTotal + convenienceFee;

  return (
    <div className="fare-summary">
      <h3 className="section-title">Fare summary</h3>

      <div className="ticket-stub">
        <div className="ticket-stub__row ticket-stub__row--muted">
          <span>Boarding</span>
          <span>{boardingPoint?.name ?? "—"}</span>
        </div>
        <div className="ticket-stub__row ticket-stub__row--muted">
          <span>Dropping</span>
          <span>{droppingPoint?.name ?? "—"}</span>
        </div>

        <div className="ticket-stub__divider" />

        {seats.map((s) => (
          <div className="ticket-stub__row" key={s.seatId}>
            <span>Seat {s.seatNumber}</span>
            <span>₹{s.price.toFixed(2)}</span>
          </div>
        ))}

        <div className="ticket-stub__row">
          <span>Convenience fee</span>
          <span>₹{convenienceFee.toFixed(2)}</span>
        </div>

        <div className="ticket-stub__divider ticket-stub__divider--perforated" />

        <div className="ticket-stub__row ticket-stub__row--total">
          <span>Total payable</span>
          <span>₹{total.toFixed(2)}</span>
        </div>
      </div>

      <button className="btn btn--primary btn--full" onClick={onProceed} disabled={isSubmitting}>
        {isSubmitting ? "Preparing payment…" : `Proceed to pay ₹${total.toFixed(2)}`}
      </button>
    </div>
  );
}
