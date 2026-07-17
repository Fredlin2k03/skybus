/**
 * Home Page - Hero section with search, popular routes, and features.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiMapPin, FiCalendar, FiSearch, FiShield, FiWifi, FiClock, FiStar, FiArrowRight } from 'react-icons/fi';
import { routesAPI } from '../services/api';
import useBookingStore from '../store/bookingStore';

export default function Home() {
  const navigate = useNavigate();
  const { setSearchParams } = useBookingStore();
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [date, setDate] = useState('');
  const [popularRoutes, setPopularRoutes] = useState([]);
  const [sourceSuggestions, setSourceSuggestions] = useState([]);
  const [destSuggestions, setDestSuggestions] = useState([]);
  const [showSourceDropdown, setShowSourceDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);

  useEffect(() => {
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    setDate(today);
    
    // Load popular routes
    routesAPI.getPopularRoutes().then(res => {
      setPopularRoutes(res.data.slice(0, 8));
    }).catch(() => {});
  }, []);

  const searchCities = async (query, type) => {
    if (query.length < 2) {
      type === 'source' ? setSourceSuggestions([]) : setDestSuggestions([]);
      return;
    }
    try {
      const res = await routesAPI.searchCities(query);
      if (type === 'source') {
        setSourceSuggestions(res.data);
        setShowSourceDropdown(true);
      } else {
        setDestSuggestions(res.data);
        setShowDestDropdown(true);
      }
    } catch (e) {}
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!source || !destination || !date) return;
    setSearchParams({ source, destination, date });
    navigate(`/search?source=${encodeURIComponent(source)}&destination=${encodeURIComponent(destination)}&date=${date}`);
  };

  const handleRouteClick = (route) => {
    setSource(route.source_city);
    setDestination(route.destination_city);
    const today = new Date().toISOString().split('T')[0];
    setSearchParams({ source: route.source_city, destination: route.destination_city, date: today });
    navigate(`/search?source=${encodeURIComponent(route.source_city)}&destination=${encodeURIComponent(route.destination_city)}&date=${today}`);
  };

  return (
    <div>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-purple-900 text-white overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle at 25px 25px, white 2%, transparent 0%)', backgroundSize: '50px 50px' }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          <div className="text-center mb-10">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
              Travel in <span className="text-yellow-400">Comfort</span>
            </h1>
            <p className="text-lg md:text-xl text-blue-100 max-w-2xl mx-auto">
              Book premium intercity bus tickets across India. Safe, reliable, and affordable travel with SkyBus.
            </p>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-4 md:p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Source */}
                <div className="relative">
                  <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">From</label>
                  <div className="relative">
                    <FiMapPin className="absolute left-3 top-3.5 text-gray-400" />
                    <input
                      type="text"
                      value={source}
                      onChange={(e) => { setSource(e.target.value); searchCities(e.target.value, 'source'); }}
                      onFocus={() => sourceSuggestions.length > 0 && setShowSourceDropdown(true)}
                      onBlur={() => setTimeout(() => setShowSourceDropdown(false), 200)}
                      placeholder="Enter city"
                      className="input-field pl-10 text-gray-900"
                      required
                    />
                  </div>
                  {showSourceDropdown && sourceSuggestions.length > 0 && (
                    <div className="absolute z-20 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto">
                      {sourceSuggestions.map((city, i) => (
                        <button
                          key={i}
                          type="button"
                          className="block w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 transition"
                          onClick={() => { setSource(city.city); setShowSourceDropdown(false); }}
                        >
                          <span className="font-medium">{city.city}</span>
                          <span className="text-gray-400 ml-1">({city.state})</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Destination */}
                <div className="relative">
                  <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">To</label>
                  <div className="relative">
                    <FiMapPin className="absolute left-3 top-3.5 text-red-400" />
                    <input
                      type="text"
                      value={destination}
                      onChange={(e) => { setDestination(e.target.value); searchCities(e.target.value, 'destination'); }}
                      onFocus={() => destSuggestions.length > 0 && setShowDestDropdown(true)}
                      onBlur={() => setTimeout(() => setShowDestDropdown(false), 200)}
                      placeholder="Enter city"
                      className="input-field pl-10 text-gray-900"
                      required
                    />
                  </div>
                  {showDestDropdown && destSuggestions.length > 0 && (
                    <div className="absolute z-20 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto">
                      {destSuggestions.map((city, i) => (
                        <button
                          key={i}
                          type="button"
                          className="block w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-blue-50 transition"
                          onClick={() => { setDestination(city.city); setShowDestDropdown(false); }}
                        >
                          <span className="font-medium">{city.city}</span>
                          <span className="text-gray-400 ml-1">({city.state})</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Date */}
                <div>
                  <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Date</label>
                  <div className="relative">
                    <FiCalendar className="absolute left-3 top-3.5 text-gray-400" />
                    <input
                      type="date"
                      value={date}
                      onChange={(e) => setDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className="input-field pl-10 text-gray-900"
                      required
                    />
                  </div>
                </div>

                {/* Search Button */}
                <div className="flex items-end">
                  <button type="submit" className="w-full btn-primary py-3 flex items-center justify-center space-x-2">
                    <FiSearch />
                    <span>Search Buses</span>
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Why Choose SkyBus?</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { icon: FiShield, title: "Safe Travel", desc: "GPS-tracked buses with trained drivers and 24/7 helpline" },
              { icon: FiWifi, title: "Premium Comfort", desc: "WiFi, charging points, blankets, and entertainment onboard" },
              { icon: FiClock, title: "On-Time Promise", desc: "98% on-time arrival rate across all routes" },
              { icon: FiStar, title: "4.5★ Rated", desc: "Trusted by 5 lakh+ happy travelers across India" },
            ].map((feature, i) => (
              <div key={i} className="text-center p-6">
                <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="text-blue-600 text-2xl" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-500 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Routes */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">Popular Routes</h2>
          <p className="text-center text-gray-500 mb-10">Travel across India's most popular intercity routes</p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {popularRoutes.map((route) => (
              <button
                key={route.id}
                onClick={() => handleRouteClick(route)}
                className="card-hover p-5 text-left group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-gray-900 group-hover:text-blue-600 transition">
                      {route.source_city}
                    </p>
                    <p className="text-xs text-gray-400 my-1">→</p>
                    <p className="font-semibold text-gray-900 group-hover:text-blue-600 transition">
                      {route.destination_city}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">{route.distance_km} km</p>
                    <p className="text-xs text-gray-400">{Math.round(route.estimated_duration_minutes / 60)}h {route.estimated_duration_minutes % 60}m</p>
                    <FiArrowRight className="text-blue-500 mt-2 ml-auto opacity-0 group-hover:opacity-100 transition" />
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Offers Banner */}
      <section className="py-12 bg-gradient-to-r from-yellow-400 to-orange-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">🎉 New User Offer!</h2>
          <p className="text-white/90 text-lg mb-4">Get 50% OFF on your first booking. Use code: <span className="font-bold bg-white/20 px-2 py-1 rounded">WELCOME50</span></p>
          <button onClick={() => navigate('/register')} className="bg-white text-orange-600 font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition">
            Sign Up Now
          </button>
        </div>
      </section>
    </div>
  );
}
