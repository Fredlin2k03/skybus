/**
 * My Bookings Page - Lists user's booking history.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiCalendar, FiMapPin, FiClock } from 'react-icons/fi';
import { bookingsAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function MyBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchBookings();
  }, [page, filter]);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 10 };
      if (filter) params.status_filter = filter;
      const res = await bookingsAPI.getMyBookings(params);
      setBookings(res.data.bookings);
      setTotal(res.data.total);
    } catch (error) {
      toast.error('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      confirmed: 'badge-success',
      pending: 'badge-warning',
      cancelled: 'badge-danger',
      completed: 'badge-info',
    };
    return colors[status] || 'badge-info';
  };

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">My Bookings</h1>
          <select
            value={filter}
            onChange={(e) => { setFilter(e.target.value); setPage(1); }}
            className="input-field w-auto text-sm py-2"
          >
            <option value="">All Bookings</option>
            <option value="confirmed">Confirmed</option>
            <option value="pending">Pending</option>
            <option value="cancelled">Cancelled</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="card p-6 animate-pulse">
                <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : bookings.length === 0 ? (
          <div className="card p-12 text-center">
            <p className="text-5xl mb-4">🎫</p>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No bookings yet</h3>
            <p className="text-gray-500 mb-4">Start your journey by searching for buses</p>
            <Link to="/search" className="btn-primary inline-block">Search Buses</Link>
          </div>
        ) : (
          <div className="space-y-4">
            {bookings.map((item) => (
              <Link
                key={item.booking.booking_id}
                to={`/booking/${item.booking.booking_id}`}
                className="card-hover p-5 block"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-bold text-gray-900">{item.source_city} → {item.destination_city}</h3>
                      <span className={getStatusColor(item.booking.status)}>
                        {item.booking.status}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <FiCalendar size={12} /> {item.booking.travel_date}
                      </span>
                      <span className="flex items-center gap-1">
                        <FiClock size={12} /> {item.departure_time} - {item.arrival_time}
                      </span>
                      <span className="flex items-center gap-1">
                        <FiMapPin size={12} /> {item.bus_name}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      Booking ID: {item.booking.booking_id} • {item.booking.passengers.length} passenger(s)
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">₹{item.booking.total_amount}</p>
                    <p className="text-xs text-gray-400">
                      {item.payment_status === 'success' ? '✓ Paid' : item.payment_status || 'Pending'}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > 10 && (
          <div className="flex justify-center gap-2 mt-6">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="btn-secondary text-sm py-2 px-4"
            >
              Previous
            </button>
            <span className="py-2 px-4 text-sm text-gray-500">
              Page {page} of {Math.ceil(total / 10)}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(total / 10)}
              className="btn-secondary text-sm py-2 px-4"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
