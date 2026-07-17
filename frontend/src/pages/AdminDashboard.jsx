/**
 * Admin Dashboard - Management panel with stats and bookings.
 */

import React, { useState, useEffect } from 'react';
import { FiUsers, FiDollarSign, FiMap, FiTruck, FiCalendar, FiStar, FiTrendingUp } from 'react-icons/fi';
import { adminAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [bookings, setBookings] = useState([]);
  const [coupons, setCoupons] = useState([]);

  useEffect(() => {
    fetchDashboard();
  }, []);

  useEffect(() => {
    if (activeTab === 'bookings') fetchBookings();
    if (activeTab === 'coupons') fetchCoupons();
  }, [activeTab]);

  const fetchDashboard = async () => {
    try {
      const res = await adminAPI.getDashboard();
      setDashboard(res.data);
    } catch (error) {
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchBookings = async () => {
    try {
      const res = await adminAPI.getBookings({ page: 1, per_page: 20 });
      setBookings(res.data.bookings);
    } catch (error) {}
  };

  const fetchCoupons = async () => {
    try {
      const res = await adminAPI.getCoupons();
      setCoupons(res.data);
    } catch (error) {}
  };

  const toggleCoupon = async (id) => {
    try {
      await adminAPI.toggleCoupon(id);
      fetchCoupons();
      toast.success('Coupon updated');
    } catch (error) {}
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const stats = dashboard?.stats || {};

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Admin Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-sm text-gray-500">SkyBus Management Panel</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-gray-200 p-1 rounded-lg w-fit">
          {['overview', 'bookings', 'coupons'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition capitalize ${
                activeTab === tab ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: 'Total Revenue', value: `₹${(stats.total_revenue / 1000).toFixed(1)}K`, icon: FiDollarSign, color: 'text-green-600 bg-green-100' },
                { label: 'Total Bookings', value: stats.total_bookings, icon: FiCalendar, color: 'text-blue-600 bg-blue-100' },
                { label: 'Active Users', value: stats.total_users, icon: FiUsers, color: 'text-purple-600 bg-purple-100' },
                { label: 'Active Routes', value: stats.total_routes, icon: FiMap, color: 'text-orange-600 bg-orange-100' },
                { label: 'Fleet Size', value: stats.total_buses, icon: FiTruck, color: 'text-cyan-600 bg-cyan-100' },
                { label: 'Today Bookings', value: stats.today_bookings, icon: FiTrendingUp, color: 'text-emerald-600 bg-emerald-100' },
                { label: 'Avg Rating', value: `${stats.average_rating}★`, icon: FiStar, color: 'text-yellow-600 bg-yellow-100' },
                { label: 'Cancel Rate', value: `${stats.cancellation_rate}%`, icon: FiCalendar, color: 'text-red-600 bg-red-100' },
              ].map((stat, i) => (
                <div key={i} className="card p-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.color}`}>
                      <stat.icon size={18} />
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">{stat.label}</p>
                      <p className="text-lg font-bold text-gray-900">{stat.value}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recent Bookings */}
            <div className="card">
              <div className="p-4 border-b">
                <h2 className="font-semibold text-gray-900">Recent Bookings</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Booking ID</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Customer</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Route</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Date</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Amount</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(dashboard?.recent_bookings || []).map((b, i) => (
                      <tr key={i} className="border-t hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs">{b.booking_id}</td>
                        <td className="px-4 py-3">{b.user_name}</td>
                        <td className="px-4 py-3">{b.route}</td>
                        <td className="px-4 py-3">{b.travel_date}</td>
                        <td className="px-4 py-3 font-medium">₹{b.amount}</td>
                        <td className="px-4 py-3">
                          <span className={`badge ${b.status === 'confirmed' ? 'badge-success' : b.status === 'cancelled' ? 'badge-danger' : 'badge-warning'}`}>
                            {b.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* Bookings Tab */}
        {activeTab === 'bookings' && (
          <div className="card">
            <div className="p-4 border-b">
              <h2 className="font-semibold text-gray-900">All Bookings</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">ID</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Customer</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Route</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Travel Date</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">PAX</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Amount</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bookings.map((b, i) => (
                    <tr key={i} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono text-xs">{b.booking_id}</td>
                      <td className="px-4 py-3">{b.user_name}<br/><span className="text-xs text-gray-400">{b.user_email}</span></td>
                      <td className="px-4 py-3">{b.route}</td>
                      <td className="px-4 py-3">{b.travel_date}</td>
                      <td className="px-4 py-3">{b.passengers}</td>
                      <td className="px-4 py-3 font-medium">₹{b.amount}</td>
                      <td className="px-4 py-3">
                        <span className={`badge ${b.status === 'confirmed' ? 'badge-success' : b.status === 'cancelled' ? 'badge-danger' : 'badge-warning'}`}>
                          {b.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Coupons Tab */}
        {activeTab === 'coupons' && (
          <div className="card">
            <div className="p-4 border-b flex justify-between items-center">
              <h2 className="font-semibold text-gray-900">Coupons</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Code</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Description</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Discount</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Uses</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Valid Until</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Status</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-500">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {coupons.map((c) => (
                    <tr key={c.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-3 font-mono font-bold">{c.code}</td>
                      <td className="px-4 py-3 text-xs max-w-[200px] truncate">{c.description}</td>
                      <td className="px-4 py-3">
                        {c.discount_type === 'percentage' ? `${c.discount_value}%` : `₹${c.discount_value}`}
                        {c.max_discount && <span className="text-xs text-gray-400"> (max ₹{c.max_discount})</span>}
                      </td>
                      <td className="px-4 py-3">{c.current_uses}/{c.max_uses || '∞'}</td>
                      <td className="px-4 py-3">{c.valid_until}</td>
                      <td className="px-4 py-3">
                        <span className={c.is_active ? 'badge-success' : 'badge-danger'}>
                          {c.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <button onClick={() => toggleCoupon(c.id)} className="text-blue-600 text-xs hover:underline">
                          {c.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
