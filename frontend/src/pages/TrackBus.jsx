/**
 * Track Bus Page - Simulated live tracking.
 */

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FiNavigation, FiClock, FiMapPin } from 'react-icons/fi';
import { busesAPI } from '../services/api';

export default function TrackBus() {
  const { busId } = useParams();
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLocation();
    const interval = setInterval(fetchLocation, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, [busId]);

  const fetchLocation = async () => {
    try {
      const res = await busesAPI.trackBus(busId);
      setLocation(res.data);
    } catch (error) {
      // Simulated fallback
      setLocation({
        bus_id: parseInt(busId),
        latitude: 12.9716 + (Math.random() - 0.5) * 0.1,
        longitude: 77.5946 + (Math.random() - 0.5) * 0.1,
        last_updated: new Date().toISOString(),
        speed_kmph: 45 + Math.random() * 35,
        next_stop: 'Electronic City',
        eta_minutes: Math.floor(20 + Math.random() * 60),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Track Your Bus</h1>

        {loading ? (
          <div className="card p-12 text-center">
            <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-4 text-gray-500">Locating bus...</p>
          </div>
        ) : location ? (
          <div className="space-y-6">
            {/* Map placeholder */}
            <div className="card overflow-hidden">
              <div className="bg-gradient-to-br from-blue-100 to-green-100 h-64 flex items-center justify-center relative">
                <div className="text-center">
                  <FiNavigation className="text-blue-600 text-4xl mx-auto mb-2 animate-pulse" />
                  <p className="text-sm font-medium text-gray-700">Live Location</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {location.latitude.toFixed(4)}°N, {location.longitude.toFixed(4)}°E
                  </p>
                </div>
                {/* Simulated route line */}
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="h-1 bg-blue-200 rounded-full">
                    <div className="h-1 bg-blue-600 rounded-full w-3/5 transition-all duration-1000"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Location details */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card p-4 text-center">
                <FiNavigation className="text-blue-600 text-xl mx-auto mb-2" />
                <p className="text-xs text-gray-400">Speed</p>
                <p className="text-lg font-bold">{location.speed_kmph?.toFixed(0)} km/h</p>
              </div>
              <div className="card p-4 text-center">
                <FiMapPin className="text-green-600 text-xl mx-auto mb-2" />
                <p className="text-xs text-gray-400">Next Stop</p>
                <p className="text-lg font-bold">{location.next_stop}</p>
              </div>
              <div className="card p-4 text-center">
                <FiClock className="text-purple-600 text-xl mx-auto mb-2" />
                <p className="text-xs text-gray-400">ETA</p>
                <p className="text-lg font-bold">{location.eta_minutes} min</p>
              </div>
            </div>

            <div className="card p-4">
              <p className="text-xs text-gray-400">
                Last updated: {new Date(location.last_updated).toLocaleTimeString()} • Updates every 10 seconds
              </p>
              <p className="text-xs text-gray-400 mt-1">
                ⓘ This is a simulated GPS location for prototype demonstration.
              </p>
            </div>
          </div>
        ) : (
          <div className="card p-12 text-center">
            <p className="text-gray-500">Unable to track bus at this time.</p>
          </div>
        )}
      </div>
    </div>
  );
}
