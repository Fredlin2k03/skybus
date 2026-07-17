import React from "react";

/**
 * seats: selected SeatDto[] (with price)
 * passengers: { [seatId]: { passengerName, age, gender } }
 * contact: { phone, email }
 */
export default function PassengerForm({ seats, passengers, onPassengerChange, contact, onContactChange }) {
  return (
    <div className="passenger-form">
      <h3 className="section-title">Passenger details</h3>
      <div className="passenger-list">
        {seats.map((seat) => {
          const p = passengers[seat.seatId] || { passengerName: "", age: "", gender: "Male" };
          return (
            <div className="passenger-card" key={seat.seatId}>
              <div className="passenger-card__seat">Seat {seat.seatNumber}</div>
              <div className="passenger-card__fields">
                <input
                  type="text"
                  placeholder="Full name"
                  value={p.passengerName}
                  onChange={(e) => onPassengerChange(seat.seatId, { ...p, passengerName: e.target.value })}
                />
                <input
                  type="number"
                  min="1"
                  max="120"
                  placeholder="Age"
                  value={p.age}
                  onChange={(e) => onPassengerChange(seat.seatId, { ...p, age: e.target.value })}
                />
                <select
                  value={p.gender}
                  onChange={(e) => onPassengerChange(seat.seatId, { ...p, gender: e.target.value })}
                >
                  <option>Male</option>
                  <option>Female</option>
                  <option>Other</option>
                </select>
              </div>
            </div>
          );
        })}
      </div>

      <h3 className="section-title">Contact details</h3>
      <div className="contact-fields">
        <input
          type="tel"
          placeholder="Mobile number"
          value={contact.phone}
          onChange={(e) => onContactChange({ ...contact, phone: e.target.value })}
        />
        <input
          type="email"
          placeholder="Email address"
          value={contact.email}
          onChange={(e) => onContactChange({ ...contact, email: e.target.value })}
        />
      </div>
      <p className="hint-text">Your ticket and boarding details will be sent here.</p>
    </div>
  );
}
