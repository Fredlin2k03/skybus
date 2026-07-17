/**
 * User Profile Page.
 */

import React, { useState, useEffect } from 'react';
import { FiUser, FiMail, FiPhone, FiEdit2, FiSave } from 'react-icons/fi';
import { usersAPI } from '../services/api';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';

export default function Profile() {
  const { user, updateUser } = useAuthStore();
  const [editing, setEditing] = useState(false);
  const [stats, setStats] = useState(null);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    phone: user?.phone || '',
    gender: user?.gender || '',
  });

  useEffect(() => {
    usersAPI.getBookingStats().then(res => setStats(res.data)).catch(() => {});
  }, []);

  const handleSave = async () => {
    try {
      const res = await usersAPI.updateProfile(formData);
      updateUser(res.data);
      setEditing(false);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

        {/* Profile Card */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <FiUser className="text-blue-600 text-2xl" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">{user?.full_name}</h2>
                <p className="text-sm text-gray-500">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={() => editing ? handleSave() : setEditing(true)}
              className="btn-secondary text-sm flex items-center gap-1"
            >
              {editing ? <><FiSave /> Save</> : <><FiEdit2 /> Edit</>}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Full Name</label>
              {editing ? (
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="input-field text-sm"
                />
              ) : (
                <p className="font-medium">{user?.full_name}</p>
              )}
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Email</label>
              <p className="font-medium flex items-center gap-1"><FiMail size={12} /> {user?.email}</p>
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Phone</label>
              {editing ? (
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="input-field text-sm"
                />
              ) : (
                <p className="font-medium flex items-center gap-1"><FiPhone size={12} /> {user?.phone || 'Not set'}</p>
              )}
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Gender</label>
              {editing ? (
                <select
                  value={formData.gender}
                  onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  className="input-field text-sm"
                >
                  <option value="">Not specified</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              ) : (
                <p className="font-medium capitalize">{user?.gender || 'Not set'}</p>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.total_bookings}</p>
              <p className="text-xs text-gray-500">Total Bookings</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{stats.completed_trips}</p>
              <p className="text-xs text-gray-500">Completed Trips</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-purple-600">₹{stats.total_spent}</p>
              <p className="text-xs text-gray-500">Total Spent</p>
            </div>
            <div className="card p-4 text-center">
              <p className="text-2xl font-bold text-red-600">{stats.cancelled_bookings}</p>
              <p className="text-xs text-gray-500">Cancelled</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
