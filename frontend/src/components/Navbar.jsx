/**
 * Navigation bar component with responsive mobile menu.
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiTruck, FiUser, FiMenu, FiX, FiLogOut, FiList, FiSettings } from 'react-icons/fi';
import useAuthStore from '../store/authStore';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, logout, isAdmin } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
    setMobileMenuOpen(false);
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <FiTruck className="text-white text-lg" />
            </div>
            <span className="text-xl font-bold text-gray-900">
              Sky<span className="text-blue-600">Bus</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/search" className="text-gray-600 hover:text-blue-600 font-medium transition">
              Search Buses
            </Link>
            
            {isAuthenticated ? (
              <>
                <Link to="/my-bookings" className="text-gray-600 hover:text-blue-600 font-medium transition">
                  My Bookings
                </Link>
                {isAdmin() && (
                  <Link to="/admin" className="text-gray-600 hover:text-blue-600 font-medium transition">
                    Admin Panel
                  </Link>
                )}
                <div className="relative group">
                  <button className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <FiUser className="text-blue-600 text-sm" />
                    </div>
                    <span className="font-medium text-sm">{user?.full_name?.split(' ')[0]}</span>
                  </button>
                  <div className="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <Link to="/profile" className="block px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 rounded-t-lg">
                      <FiUser className="inline mr-2" /> Profile
                    </Link>
                    <Link to="/my-bookings" className="block px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50">
                      <FiList className="inline mr-2" /> My Bookings
                    </Link>
                    <button onClick={handleLogout} className="block w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-b-lg">
                      <FiLogOut className="inline mr-2" /> Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/login" className="text-gray-600 hover:text-blue-600 font-medium transition">
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-sm py-2 px-4">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <div className="px-4 py-3 space-y-2">
            <Link to="/search" className="block py-2 text-gray-700 font-medium" onClick={() => setMobileMenuOpen(false)}>
              Search Buses
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/my-bookings" className="block py-2 text-gray-700 font-medium" onClick={() => setMobileMenuOpen(false)}>
                  My Bookings
                </Link>
                <Link to="/profile" className="block py-2 text-gray-700 font-medium" onClick={() => setMobileMenuOpen(false)}>
                  Profile
                </Link>
                {isAdmin() && (
                  <Link to="/admin" className="block py-2 text-gray-700 font-medium" onClick={() => setMobileMenuOpen(false)}>
                    Admin Panel
                  </Link>
                )}
                <button onClick={handleLogout} className="block py-2 text-red-600 font-medium">
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="block py-2 text-gray-700 font-medium" onClick={() => setMobileMenuOpen(false)}>
                  Login
                </Link>
                <Link to="/register" className="block py-2 text-blue-600 font-medium" onClick={() => setMobileMenuOpen(false)}>
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
