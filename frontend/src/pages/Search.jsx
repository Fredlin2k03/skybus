/**
 * Search Results Page - Shows available buses with filters.
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { FiFilter, FiClock, FiStar, FiWifi, FiZap, FiDroplet } from 'react-icons/fi';
import { routesAPI } from '../services/api';
import useBookingStore from '../store/bookingStore';
import useAuthStore from '../store/authStore';
import toast from 'react-hot-toast';

export default function Search() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const { setSearchResults, selectSchedule } = useBookingStore();
  
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    busType: '',
    departureTime: '',
    priceMin: '',
    priceMax: '',
    sortBy: 'departure',
  });
  const [showFilters, setShowFilters] = useState(false);

  const source = searchParams.get('source') || '';
  const destination = searchParams.get('destination') || '';
  const date = searchParams.get('date') || '';

  useEffect(() => {
    if (source && destination && date) {
      fetchResults();
    }
  }, [source, destination, date, filters.busType, filters.departureTime, filters.sortBy]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const params = {
        source,
        destination,
        date,
        sort_by: filters.sortBy,
      };
      if (filters.busType) params.bus_type = filters.busType;
      if (filters.departureTime) params.departure_time = filters.departureTime;
      if (filters.priceMin) params.price_min = filters.priceMin;
      if (filters.priceMax) params.price_max = filters.priceMax;
      
      const res = await routesAPI.searchBuses(params);
      setResults(res.data);
      setSearchResults(res.data);
    } catch (error) {
      toast.error('Failed to search buses');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectBus = (schedule) => {
    if (!isAuthenticated) {
      toast.error('Please login to book tickets');
      navigate('/login');
      return;
    }
    selectSchedule(schedule);
    navigate(`/seats/${schedule.schedule_id}?date=${date}`);
  };

  const formatDuration = (minutes) => {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return `${h}h ${m}m`;
  };

  const getAmenityIcon = (name) => {
    const icons = {
      'WiFi': '📶', 'Charging Point': '🔌', 'Blanket': '🛏️',
      'Water Bottle': '💧', 'Entertainment': '🎬', 'GPS Tracking': '📍',
      'Reading Light': '💡', 'Air Conditioning': '❄️', 'Snacks': '🍿',
    };
    return icons[name] || '✓';
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {source} → {destination}
              </h1>
              <p className="text-sm text-gray-500">
                {new Date(date).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                {' • '}{results.length} bus{results.length !== 1 ? 'es' : ''} found
              </p>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary text-sm flex items-center space-x-1"
            >
              <FiFilter /> <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar */}
          <aside className={`lg:w-64 ${showFilters ? 'block' : 'hidden lg:block'}`}>
            <div className="card p-5 sticky top-20">
              <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>
              
              {/* Sort */}
              <div className="mb-5">
                <label className="text-sm font-medium text-gray-600 mb-2 block">Sort By</label>
                <select
                  value={filters.sortBy}
                  onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                  className="input-field text-sm py-2"
                >
                  <option value="departure">Departure Time</option>
                  <option value="price">Price: Low to High</option>
                  <option value="duration">Duration</option>
                  <option value="rating">Rating</option>
                </select>
              </div>
              
              {/* Bus Type */}
              <div className="mb-5">
                <label className="text-sm font-medium text-gray-600 mb-2 block">Bus Type</label>
                <select
                  value={filters.busType}
                  onChange={(e) => setFilters({ ...filters, busType: e.target.value })}
                  className="input-field text-sm py-2"
                >
                  <option value="">All Types</option>
                  <option value="AC Sleeper">AC Sleeper</option>
                  <option value="AC Seater">AC Seater</option>
                  <option value="Non-AC Sleeper">Non-AC Sleeper</option>
                  <option value="Non-AC Seater">Non-AC Seater</option>
                  <option value="Volvo Multi-Axle">Volvo Multi-Axle</option>
                </select>
              </div>
              
              {/* Departure Time */}
              <div className="mb-5">
                <label className="text-sm font-medium text-gray-600 mb-2 block">Departure</label>
                <div className="space-y-2">
                  {[
                    { value: '', label: 'Any Time' },
                    { value: 'morning', label: '🌅 Morning (6-12)' },
                    { value: 'afternoon', label: '☀️ Afternoon (12-5)' },
                    { value: 'evening', label: '🌆 Evening (5-9)' },
                    { value: 'night', label: '🌙 Night (9-6)' },
                  ].map((opt) => (
                    <label key={opt.value} className="flex items-center text-sm cursor-pointer">
                      <input
                        type="radio"
                        name="departure"
                        value={opt.value}
                        checked={filters.departureTime === opt.value}
                        onChange={(e) => setFilters({ ...filters, departureTime: e.target.value })}
                        className="mr-2"
                      />
                      {opt.label}
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Price Range */}
              <div className="mb-5">
                <label className="text-sm font-medium text-gray-600 mb-2 block">Price Range</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={filters.priceMin}
                    onChange={(e) => setFilters({ ...filters, priceMin: e.target.value })}
                    className="input-field text-sm py-2 w-1/2"
                  />
                  <input
                    type="number"
                    placeholder="Max"
                    value={filters.priceMax}
                    onChange={(e) => setFilters({ ...filters, priceMax: e.target.value })}
                    className="input-field text-sm py-2 w-1/2"
                  />
                </div>
                <button onClick={fetchResults} className="text-blue-600 text-xs mt-1 hover:underline">Apply</button>
              </div>
            </div>
          </aside>

          {/* Results */}
          <div className="flex-1">
            {loading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="card p-6 animate-pulse">
                    <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : results.length === 0 ? (
              <div className="card p-12 text-center">
                <p className="text-6xl mb-4">🚌</p>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No buses found</h3>
                <p className="text-gray-500">Try different dates or routes.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((bus) => (
                  <div key={bus.schedule_id} className="card-hover p-5 md:p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      {/* Bus Info */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-bold text-gray-900">{bus.bus.name}</h3>
                          {bus.rating && (
                            <span className="badge-success flex items-center gap-1">
                              <FiStar size={10} /> {bus.rating}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 mb-3">
                          {bus.bus.bus_type.category} • {bus.bus.bus_type.seat_layout} Layout
                        </p>
                        
                        {/* Timing */}
                        <div className="flex items-center gap-4">
                          <div>
                            <p className="text-lg font-bold text-gray-900">{bus.departure_time}</p>
                            <p className="text-xs text-gray-400">{source}</p>
                          </div>
                          <div className="flex-1 px-3">
                            <div className="relative">
                              <div className="border-t-2 border-dashed border-gray-300"></div>
                              <p className="absolute -top-3 left-1/2 -translate-x-1/2 bg-white px-2 text-xs text-gray-400">
                                {formatDuration(bus.duration_minutes)}
                              </p>
                            </div>
                          </div>
                          <div>
                            <p className="text-lg font-bold text-gray-900">{bus.arrival_time}</p>
                            <p className="text-xs text-gray-400">{destination}</p>
                          </div>
                        </div>
                        
                        {/* Amenities */}
                        <div className="flex flex-wrap gap-2 mt-3">
                          {bus.amenities.slice(0, 5).map((amenity, i) => (
                            <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                              {getAmenityIcon(amenity)} {amenity}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      {/* Price & Book */}
                      <div className="text-right md:min-w-[160px]">
                        <p className="text-sm text-gray-400 mb-1">Starting from</p>
                        <p className="text-2xl font-bold text-gray-900">₹{bus.base_fare}</p>
                        {bus.sleeper_fare && (
                          <p className="text-xs text-gray-400">Sleeper: ₹{bus.sleeper_fare}</p>
                        )}
                        <div className="mt-2">
                          <span className={`text-sm font-medium ${bus.available_seats <= 5 ? 'text-red-600' : 'text-green-600'}`}>
                            {bus.available_seats} seats left
                          </span>
                        </div>
                        <button
                          onClick={() => handleSelectBus(bus)}
                          className="btn-primary text-sm mt-3 w-full"
                          disabled={bus.available_seats === 0}
                        >
                          {bus.available_seats === 0 ? 'Sold Out' : 'Select Seats'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
