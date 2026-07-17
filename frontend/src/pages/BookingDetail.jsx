/**
 * Booking Detail Page - Shows full booking info with cancel option.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiMapPin, FiCalendar, FiClock, FiUser, FiPhone, FiMail } from 'react-icons/fi';
import { bookingsAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function BookingDetail() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [cancelReason, setCancelReason] = useState('');

  useEffect(() => {
    fetchBooking();
  }, [bookingId]);

  const fetchBooking = async () => {
    try {
      const res = await bookingsAPI.getBooking(bookingId);
      setData(res.data);
    } catch (error) {
      toast.error('Booking not found');
      navigate('/my-bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    setCancelling(true);
    try {
      const res = await bookingsAPI.cancel(bookingId, { reason: cancelReason });
      toast.success(`Booking cancelled. Refund: ₹${res.data.refund_amount}`);
      setShowCancelModal(false);
      fetchBooking();
    } catch (error) {
      toast.error(error.message || 'Failed to cancel booking');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!data) return null;

  const { booking } = data;

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{data.source_city} → {data.destination_city}</h1>
              <p className="text-gray-500 text-sm">Booking ID: <span className="font-mono font-medium">{booking.booking_id}</span></p>
            </div>
            <span className={`${booking.status === 'confirmed' ? 'badge-success' : booking.status === 'cancelled' ? 'badge-danger' : 'badge-warning'} text-sm px-3 py-1`}>
              {booking.status.toUpperCase()}
            </span>
          </div>

          {/* Route info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y">
            <div>
              <p className="text-xs text-gray-400">Date</p>
              <p className="font-medium flex items-center gap-1"><FiCalendar size={12} /> {booking.travel_date}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Departure</p>
              <p className="font-medium flex items-center gap-1"><FiClock size={12} /> {data.departure_time}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Bus</p>
              <p className="font-medium">{data.bus_name}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Type</p>
              <p className="font-medium">{data.bus_type}</p>
            </div>
          </div>

          {/* Boarding/Dropping */}
          <div className="grid grid-cols-2 gap-4 pt-4">
            <div>
              <p className="text-xs text-gray-400 flex items-center gap-1"><FiMapPin size={10} /> Boarding Point</p>
              <p className="font-medium text-sm">{data.boarding_point}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 flex items-center gap-1"><FiMapPin size={10} /> Dropping Point</p>
              <p className="font-medium text-sm">{data.dropping_point}</p>
            </div>
          </div>
        </div>

        {/* Passengers */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2"><FiUser /> Passengers</h2>
          <div className="space-y-3">
            {booking.passengers.map((p, i) => (
              <div key={i} className="flex justify-between items-center py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-xs text-gray-400">{p.gender}, {p.age} yrs • Seat {p.seat_number} ({p.seat_type})</p>
                </div>
                <p className="font-medium">₹{p.seat_fare}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Fare Breakdown */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4">Fare Details</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-600">Base Fare</span><span>₹{booking.base_amount}</span></div>
            {booking.discount_amount > 0 && (
              <div className="flex justify-between text-green-600"><span>Discount ({booking.coupon_code})</span><span>- ₹{booking.discount_amount}</span></div>
            )}
            <div className="flex justify-between"><span className="text-gray-600">GST (5%)</span><span>₹{booking.gst_amount}</span></div>
            <div className="border-t pt-2 flex justify-between font-bold text-lg">
              <span>Total Paid</span><span className="text-blue-600">₹{booking.total_amount}</span>
            </div>
            {booking.refund_amount && (
              <div className="flex justify-between text-green-600"><span>Refund Amount</span><span>₹{booking.refund_amount}</span></div>
            )}
          </div>
        </div>

        {/* Contact */}
        <div className="card p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-3">Contact Details</h2>
          <div className="flex gap-6 text-sm">
            <span className="flex items-center gap-1 text-gray-600"><FiMail size={12} /> {booking.contact_email}</span>
            <span className="flex items-center gap-1 text-gray-600"><FiPhone size={12} /> {booking.contact_phone}</span>
          </div>
        </div>

        {/* Actions */}
        {booking.status === 'confirmed' && (
          <div className="flex gap-3">
            <button onClick={() => setShowCancelModal(true)} className="btn-danger">
              Cancel Booking
            </button>
            <button onClick={() => navigate(`/track/${data.bus_id || 1}`)} className="btn-secondary">
              Track Bus
            </button>
          </div>
        )}

        {/* Cancel Modal */}
        {showCancelModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
            <div className="bg-white rounded-xl p-6 max-w-sm w-full">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Cancel Booking?</h3>
              <p className="text-sm text-gray-500 mb-4">Cancellation charges may apply based on timing.</p>
              <textarea
                placeholder="Reason for cancellation (optional)"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                className="input-field text-sm mb-4"
                rows={3}
              />
              <div className="flex gap-3">
                <button onClick={() => setShowCancelModal(false)} className="btn-secondary flex-1">
                  Keep Booking
                </button>
                <button onClick={handleCancel} disabled={cancelling} className="btn-danger flex-1">
                  {cancelling ? 'Cancelling...' : 'Confirm Cancel'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
