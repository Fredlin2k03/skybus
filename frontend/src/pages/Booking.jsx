/**
 * Booking Page - Passenger details, contact info, coupon, and pricing summary.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiTag, FiX } from 'react-icons/fi';
import { bookingsAPI, couponsAPI } from '../services/api';
import useBookingStore from '../store/bookingStore';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';

export default function Booking() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const {
    selectedSchedule, selectedSeats, seatLayout,
    baseFare, discount, gst, totalAmount, couponCode, couponApplied,
    applyCoupon, removeCoupon, calculatePricing, setCurrentBooking
  } = useBookingStore();

  const [passengers, setPassengers] = useState([]);
  const [contactEmail, setContactEmail] = useState(user?.email || '');
  const [contactPhone, setContactPhone] = useState(user?.phone || '');
  const [gstNumber, setGstNumber] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [showGst, setShowGst] = useState(false);
  const [couponInput, setCouponInput] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedSchedule || selectedSeats.length === 0) {
      navigate('/');
      return;
    }
    // Initialize passenger forms
    setPassengers(selectedSeats.map(seat => ({
      name: '',
      age: '',
      gender: 'male',
      seat_number: seat.seatNumber,
      seat_type: seat.seatType,
    })));
    calculatePricing();
  }, []);

  const updatePassenger = (index, field, value) => {
    const updated = [...passengers];
    updated[index] = { ...updated[index], [field]: value };
    setPassengers(updated);
  };

  const handleApplyCoupon = async () => {
    if (!couponInput.trim()) return;
    try {
      const res = await couponsAPI.validate(couponInput, baseFare);
      if (res.data.valid) {
        applyCoupon(couponInput.toUpperCase(), res.data.discount_amount);
        toast.success(res.data.message);
      } else {
        toast.error(res.data.message);
      }
    } catch (error) {
      toast.error('Failed to validate coupon');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate passengers
    for (let i = 0; i < passengers.length; i++) {
      if (!passengers[i].name || !passengers[i].age) {
        toast.error(`Please fill details for Passenger ${i + 1}`);
        return;
      }
      if (parseInt(passengers[i].age) < 1 || parseInt(passengers[i].age) > 120) {
        toast.error(`Invalid age for Passenger ${i + 1}`);
        return;
      }
    }
    
    if (!contactEmail || !contactPhone) {
      toast.error('Please provide contact information');
      return;
    }
    
    if (!/^[6-9]\d{9}$/.test(contactPhone)) {
      toast.error('Please enter a valid 10-digit mobile number');
      return;
    }

    setLoading(true);
    try {
      // Determine boarding and dropping stops
      const boardingStopId = selectedSchedule?.bus?.id ? 1 : 1; // Use first stop as default
      const droppingStopId = selectedSchedule?.bus?.id ? 3 : 3; // Use last stop as default
      
      const bookingData = {
        schedule_id: selectedSchedule.schedule_id,
        travel_date: new URLSearchParams(window.location.search).get('date') || 
                     new URL(document.referrer || window.location.href).searchParams.get('date') ||
                     localStorage.getItem('skybus_travel_date') || 
                     new Date().toISOString().split('T')[0],
        boarding_stop_id: boardingStopId,
        dropping_stop_id: droppingStopId,
        passengers: passengers.map(p => ({
          ...p,
          age: parseInt(p.age),
        })),
        contact_email: contactEmail,
        contact_phone: contactPhone,
        coupon_code: couponApplied ? couponCode : null,
        gst_number: showGst ? gstNumber : null,
        company_name: showGst ? companyName : null,
      };
      
      const res = await bookingsAPI.create(bookingData);
      setCurrentBooking(res.data);
      toast.success('Booking created! Proceeding to payment...');
      navigate(`/payment/${res.data.booking_id}`);
    } catch (error) {
      toast.error(error.message || 'Failed to create booking');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedSchedule) return null;

  return (
    <div className="bg-gray-50 min-h-screen py-6">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Complete Your Booking</h1>

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Passenger Details */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FiUser /> Passenger Details
                </h2>
                
                {passengers.map((passenger, index) => (
                  <div key={index} className="mb-6 pb-4 border-b border-gray-100 last:border-0 last:mb-0 last:pb-0">
                    <h3 className="text-sm font-medium text-gray-600 mb-3">
                      Passenger {index + 1} — Seat {passenger.seat_number} ({passenger.seat_type})
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <input
                        type="text"
                        placeholder="Full Name"
                        value={passenger.name}
                        onChange={(e) => updatePassenger(index, 'name', e.target.value)}
                        className="input-field text-sm"
                        required
                      />
                      <input
                        type="number"
                        placeholder="Age"
                        value={passenger.age}
                        onChange={(e) => updatePassenger(index, 'age', e.target.value)}
                        className="input-field text-sm"
                        min="1"
                        max="120"
                        required
                      />
                      <select
                        value={passenger.gender}
                        onChange={(e) => updatePassenger(index, 'gender', e.target.value)}
                        className="input-field text-sm"
                      >
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                ))}
              </div>

              {/* Contact Information */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
                <p className="text-xs text-gray-400 mb-3">Booking confirmation will be sent to this email & phone.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <input
                    type="email"
                    placeholder="Email Address"
                    value={contactEmail}
                    onChange={(e) => setContactEmail(e.target.value)}
                    className="input-field text-sm"
                    required
                  />
                  <input
                    type="tel"
                    placeholder="Mobile Number (10 digits)"
                    value={contactPhone}
                    onChange={(e) => setContactPhone(e.target.value)}
                    className="input-field text-sm"
                    pattern="[6-9][0-9]{9}"
                    required
                  />
                </div>
                
                {/* GST */}
                <div className="mt-4">
                  <button type="button" onClick={() => setShowGst(!showGst)} className="text-blue-600 text-sm hover:underline">
                    {showGst ? 'Remove GST Details' : '+ Add GST Details (for business travel)'}
                  </button>
                  {showGst && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
                      <input
                        type="text"
                        placeholder="GST Number"
                        value={gstNumber}
                        onChange={(e) => setGstNumber(e.target.value)}
                        className="input-field text-sm"
                      />
                      <input
                        type="text"
                        placeholder="Company Name"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        className="input-field text-sm"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Coupon */}
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FiTag /> Apply Coupon
                </h2>
                {couponApplied ? (
                  <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-4 py-3">
                    <div>
                      <span className="font-semibold text-green-800">{couponCode}</span>
                      <span className="text-sm text-green-600 ml-2">- ₹{discount} off</span>
                    </div>
                    <button type="button" onClick={removeCoupon} className="text-red-500 hover:text-red-700">
                      <FiX size={18} />
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Enter coupon code"
                      value={couponInput}
                      onChange={(e) => setCouponInput(e.target.value.toUpperCase())}
                      className="input-field text-sm flex-1"
                    />
                    <button type="button" onClick={handleApplyCoupon} className="btn-secondary text-sm">
                      Apply
                    </button>
                  </div>
                )}
                <p className="text-xs text-gray-400 mt-2">Try: WELCOME50, SKYBUS100, SUMMER25</p>
              </div>
            </div>

            {/* Pricing Summary Sidebar */}
            <div>
              <div className="card p-5 sticky top-20">
                <h3 className="font-semibold text-gray-900 mb-4">Fare Summary</h3>
                
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Base Fare ({selectedSeats.length} seat{selectedSeats.length > 1 ? 's' : ''})</span>
                    <span>₹{baseFare}</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount</span>
                      <span>- ₹{discount}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-gray-600">GST (5%)</span>
                    <span>₹{gst}</span>
                  </div>
                  <div className="border-t pt-2 mt-2 flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span className="text-blue-600">₹{totalAmount}</span>
                  </div>
                </div>
                
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full mt-4"
                >
                  {loading ? 'Processing...' : 'Proceed to Payment'}
                </button>
                
                <p className="text-xs text-gray-400 text-center mt-3">
                  By proceeding, you agree to our Terms of Service
                </p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
