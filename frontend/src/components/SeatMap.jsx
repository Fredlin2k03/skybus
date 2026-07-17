import React from "react";

/**
 * Renders lower/upper deck sleeper layout. Each seat shows its price.
 * seats: [{ seatId, seatNumber, deck, seatType, rowPosition, columnPosition, price, isBooked }]
 */
export default function SeatMap({ seats, selectedSeatIds, onToggleSeat, maxSeats = 6 }) {
  const decks = ["Lower", "Upper"].filter((d) => seats.some((s) => s.deck === d));

  const seatState = (seat) => {
    if (seat.isBooked) return "booked";
    if (selectedSeatIds.includes(seat.seatId)) return "selected";
    return "available";
  };

  const handleClick = (seat) => {
    if (seat.isBooked) return;
    const isSelected = selectedSeatIds.includes(seat.seatId);
    if (!isSelected && selectedSeatIds.length >= maxSeats) return;
    onToggleSeat(seat.seatId);
  };

  return (
    <div className="seatmap">
      <div className="seatmap__legend">
        <span className="legend-item"><i className="dot dot--available" />Available</span>
        <span className="legend-item"><i className="dot dot--selected" />Selected</span>
        <span className="legend-item"><i className="dot dot--booked" />Booked</span>
      </div>

      <div className="seatmap__decks">
        {decks.map((deck) => {
          const deckSeats = seats.filter((s) => s.deck === deck);
          const rows = [...new Set(deckSeats.map((s) => s.rowPosition))].sort((a, b) => a - b);

          return (
            <div className="seatmap__deck" key={deck}>
              <div className="seatmap__deck-label">{deck} Deck</div>
              <div className="seatmap__grid">
                {rows.map((row) => (
                  <div className="seatmap__row" key={row}>
                    {deckSeats
                      .filter((s) => s.rowPosition === row)
                      .sort((a, b) => a.columnPosition - b.columnPosition)
                      .map((seat) => (
                        <button
                          key={seat.seatId}
                          type="button"
                          className={`seat seat--${seatState(seat)}`}
                          disabled={seat.isBooked}
                          onClick={() => handleClick(seat)}
                          title={`${seat.seatNumber} · ₹${seat.price}`}
                        >
                          <span className="seat__number">{seat.seatNumber}</span>
                          <span className="seat__price">₹{seat.price}</span>
                        </button>
                      ))}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
