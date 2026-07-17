/**
 * Seat Selection Page - Interactive seat map for selecting seats.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { FiInfo } from 'react-icons/fi';
import { busesAPI } from '../services/api';
import useBookingStore from '../store/bookingStore';
import toast from 'react-hot-toast';

export default function SeatSelection() {
  const { scheduleId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const date = searchParams.get('date');
  
  const { selectedSchedule, seatLayout, setSeatLayout, selectedSeats, toggleSeat, calculatePricing } = useBookingStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSeatLayout();
  }, [scheduleId, date]);

  useEffect(() => {
    calculatePricing();
  }, [selectedSeats]);

  const fetchSeatLayout = async () => {
    try {
      const res = await busesAPI.getSeatLayout(scheduleId, date);
      setSeatLayout(res.data);
    } catch (error) {
      toast.error('Failed to load seat layout');
    } finally {
      setLoading(false);
    }
  };

  const handleSeatClick = (seat) => {
    if (seat.is_booked || seat.is_blocked) return;
    
    const fare = seat.seat_type === 'sleeper' && seatLayout.sleeper_fare
      ? seatLayout.sleeper_fare * seat.price_multiplier
      : seatLayout.base_fare * seat.price_multiplier;
    
    toggleSeat(seat.seat_number, seat.seat_type, Math.round(fare));
  };

  const getSeatClass = (seat) => {
    if (seat.is_booked) return 'seat-booked';
    if (selectedSeats.find(s => s.seatNumber === seat.seat_number)) return 'seat-selected';
    if (seat.is_ladies_only) return 'seat-ladies';
    return 'seat-available';
  };

  const proceedToBooking = () => {
    if (selectedSeats.length === 0) {
      toast.error('Please select at least one seat');
      return;
    }
    navigate('/booking');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!seatLayout) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Seat layout not available</p>
      </div>
    );
  }

  // Group seats by deck
  const lowerDeck = seatLayout.seats.filter(s => s.deck === 'lower');
  const upperDeck = seatLayout.seats.filter(s => s.deck === 'upper');

  // Group by rows
  const groupByRows = (seats) => {
    const rows = {};
    seats.forEach(seat => {
      if (!rows[seat.row_number]) rows[seat.row_number] = [];
      rows[seat.row_number].push(seat);
    });
    return Object.entries(rows).sort(([a], [b]) => a - b);
  };

  const renderSeatGrid = (seats, deckLabel) => {
    const rows = groupByRows(seats);
    const isSleeper = seats[0]?.seat_type === 'sleeper';
    
    return (
      <div className="mb-6">
        {deckLabel && <h4 className="text-sm font-semibold text-gray-600 mb-3">{deckLabel}</h4>}
        <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          {/* Driver indicator for lower deck */}
          {deckLabel !== 'Upper Deck' && (
            <div className="flex justify-end mb-4">
              <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center text-xs text-gray-600">
                🚌
              </div>
            </div>
          )}
          
          <div className="space-y-2">
            {rows.map(([rowNum, rowSeats]) => (
              <div key={rowNum} className="flex items-center justify-center gap-1">
                {/* Left seats */}
                <div className="flex gap-1">
                  {rowSeats.filter(s => s.column_number <= 2).map(seat => (
                    <button
                      key={seat.seat_number}
                      onClick={() => handleSeatClick(seat)}
                      className={`${isSleeper ? 'sleeper-seat' : 'seat'} ${getSeatClass(seat)}`}
                      disabled={seat.is_booked || seat.is_blocked}
                      title={`${seat.seat_number} - ₹${Math.round(
                        (seat.seat_type === 'sleeper' && seatLayout.sleeper_fare ? seatLayout.sleeper_fare : seatLayout.base_fare) * seat.price_multiplier
                      )}`}
                    >
                      {seat.seat_number}
                    </button>
                  ))}
                </div>
                
                {/* Aisle */}
                <div className="w-8"></div>
                
                {/* Right seats */}
                <div className="flex gap-1">
                  {rowSeats.filter(s => s.column_number > 2).map(seat => (
                    <button
                      key={seat.seat_number}
                      onClick={() => handleSeatClick(seat)}
                      className={`${isSleeper ? 'sleeper-seat' : 'seat'} ${getSeatClass(seat)}`}
                      disabled={seat.is_booked || seat.is_blocked}
                      title={`${seat.seat_number} - ₹${Math.round(
                        (seat.seat_type === 'sleeper' && seatLayout.sleeper_fare ? seatLayout.sleeper_fare : seatLayout.base_fare) * seat.price_multiplier
                      )}`}
                    >
                      {seat.seat_number}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const totalFare = selectedSeats.reduce((sum, s) => sum + s.fare, 0);

  return (
    <div className="bg-gray-50 min-h-screen py-6">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Select Your Seats</h1>
          <p className="text-gray-500">{seatLayout.bus_name} • {seatLayout.bus_type}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Seat Map */}
          <div className="lg:col-span-2">
            <div className="card p-6">
              {/* Legend */}
              <div className="flex flex-wrap gap-4 mb-6 pb-4 border-b">
                <div className="flex items-center gap-2 text-xs">
                  <div className="seat seat-available !w-6 !h-6 !text-[8px]"></div>
                  <span>Available</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="seat seat-selected !w-6 !h-6 !text-[8px]"></div>
                  <span>Selected</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="seat seat-booked !w-6 !h-6 !text-[8px]"></div>
                  <span>Booked</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="seat seat-ladies !w-6 !h-6 !text-[8px]"></div>
                  <span>Ladies</span>
                </div>
              </div>

              {/* Seat Grid */}
              {lowerDeck.length > 0 && renderSeatGrid(lowerDeck, seatLayout.has_upper_deck ? 'Lower Deck' : null)}
              {upperDeck.length > 0 && renderSeatGrid(upperDeck, 'Upper Deck')}
            </div>
          </div>

          {/* Booking Summary */}
          <div>
            <div className="card p-5 sticky top-20">
              <h3 className="font-semibold text-gray-900 mb-4">Booking Summary</h3>
              
              {selectedSeats.length === 0 ? (
                <div className="text-center py-6">
                  <FiInfo className="mx-auto text-3xl text-gray-300 mb-2" />
                  <p className="text-sm text-gray-400">Select seats to continue</p>
                </div>
              ) : (
                <>
                  <div className="space-y-2 mb-4">
                    {selectedSeats.map(seat => (
                      <div key={seat.seatNumber} className="flex justify-between items-center py-1.5 border-b border-gray-100">
                        <div>
                          <span className="font-medium text-sm">Seat {seat.seatNumber}</span>
                          <span className="text-xs text-gray-400 ml-2 capitalize">{seat.seatType}</span>
                        </div>
                        <span className="font-medium text-sm">₹{seat.fare}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="border-t pt-3 mb-4">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-900">Total</span>
                      <span className="text-xl font-bold text-blue-600">₹{totalFare}</span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {selectedSeats.length} seat{selectedSeats.length > 1 ? 's' : ''} • GST extra
                    </p>
                  </div>
                  
                  <button
                    onClick={proceedToBooking}
                    className="btn-primary w-full"
                  >
                    Continue to Booking
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
