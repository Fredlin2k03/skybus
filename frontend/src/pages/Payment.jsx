/**
 * Payment Page - Handles Razorpay integration and payment simulation.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiCheckCircle, FiCreditCard, FiShield } from 'react-icons/fi';
import { paymentsAPI, bookingsAPI } from '../services/api';
import useBookingStore from '../store/bookingStore';
import toast from 'react-hot-toast';

export default function Payment() {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const { currentBooking, resetBooking } = useBookingStore();
  const [loading, setLoading] = useState(false);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [booking, setBooking] = useState(currentBooking);

  useEffect(() => {
    if (!booking && bookingId) {
      fetchBooking();
    }
  }, [bookingId]);

  const fetchBooking = async () => {
    try {
      const res = await bookingsAPI.getBooking(bookingId);
      setBooking(res.data.booking);
    } catch (error) {
      toast.error('Failed to load booking details');
      navigate('/my-bookings');
    }
  };

  const handleRazorpayPayment = async () => {
    setLoading(true);
    try {
      // Create Razorpay order
      const orderRes = await paymentsAPI.createOrder({ booking_id: bookingId });
      const { order_id, amount, currency, key_id } = orderRes.data;

      // Check if Razorpay is loaded
      if (window.Razorpay) {
        const options = {
          key: key_id,
          amount: amount,
          currency: currency,
          name: 'SkyBus',
          description: `Booking ${bookingId}`,
          order_id: order_id,
          handler: async (response) => {
            try {
              await paymentsAPI.verify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                booking_id: bookingId,
              });
              setPaymentSuccess(true);
              resetBooking();
              toast.success('Payment successful! Booking confirmed.');
            } catch (error) {
              toast.error('Payment verification failed');
            }
          },
          prefill: {
            email: booking?.contact_email || '',
            contact: booking?.contact_phone || '',
          },
          theme: { color: '#2563eb' },
        };
        
        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        // Razorpay not loaded, simulate
        handleSimulatePayment();
      }
    } catch (error) {
      toast.error('Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePayment = async () => {
    setLoading(true);
    try {
      await paymentsAPI.simulateSuccess({ booking_id: bookingId });
      setPaymentSuccess(true);
      resetBooking();
      toast.success('Payment successful! Booking confirmed.');
    } catch (error) {
      toast.error('Payment simulation failed');
    } finally {
      setLoading(false);
    }
  };

  if (paymentSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="card p-8 md:p-12 text-center max-w-md w-full">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <FiCheckCircle className="text-green-600 text-4xl" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Booking Confirmed!</h1>
          <p className="text-gray-500 mb-2">Your booking ID is:</p>
          <p className="text-xl font-bold text-blue-600 mb-6">{bookingId}</p>
          <p className="text-sm text-gray-400 mb-6">
            A confirmation email has been sent to your registered email address.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => navigate(`/booking/${bookingId}`)}
              className="btn-primary w-full"
            >
              View Booking Details
            </button>
            <button
              onClick={() => navigate('/my-bookings')}
              className="btn-secondary w-full"
            >
              Go to My Bookings
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-lg mx-auto px-4">
        <div className="card p-6 md:p-8">
          <div className="text-center mb-6">
            <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <FiCreditCard className="text-blue-600 text-2xl" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Payment</h1>
            <p className="text-gray-500 text-sm mt-1">Booking ID: {bookingId}</p>
          </div>

          {/* Amount */}
          <div className="bg-gray-50 rounded-xl p-4 mb-6 text-center">
            <p className="text-sm text-gray-500">Amount to Pay</p>
            <p className="text-3xl font-bold text-gray-900">
              ₹{booking?.total_amount || 0}
            </p>
          </div>

          {/* Payment Options */}
          <div className="space-y-3 mb-6">
            <button
              onClick={handleRazorpayPayment}
              disabled={loading}
              className="btn-primary w-full py-4 text-lg"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Processing...
                </span>
              ) : (
                'Pay with Razorpay'
              )}
            </button>
            
            <button
              onClick={handleSimulatePayment}
              disabled={loading}
              className="btn-secondary w-full py-3"
            >
              Simulate Payment (Dev Mode)
            </button>
          </div>

          {/* Security badge */}
          <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
            <FiShield />
            <span>256-bit SSL encrypted payment</span>
          </div>
        </div>
      </div>
    </div>
  );
}
