/**
 * Booking Store - Manages the booking flow state.
 */

import { create } from 'zustand';

const useBookingStore = create((set, get) => ({
  // Search state
  searchParams: {
    source: '',
    destination: '',
    date: '',
  },
  searchResults: [],
  
  // Selected bus/schedule
  selectedSchedule: null,
  
  // Seat selection
  seatLayout: null,
  selectedSeats: [],
  
  // Passenger info
  passengers: [],
  contactInfo: { email: '', phone: '' },
  
  // Pricing
  baseFare: 0,
  discount: 0,
  gst: 0,
  totalAmount: 0,
  couponCode: '',
  couponApplied: false,
  
  // Booking result
  currentBooking: null,
  
  // Actions
  setSearchParams: (params) => set({ searchParams: params }),
  setSearchResults: (results) => set({ searchResults: results }),
  
  selectSchedule: (schedule) => set({ selectedSchedule: schedule, selectedSeats: [] }),
  
  setSeatLayout: (layout) => set({ seatLayout: layout }),
  
  toggleSeat: (seatNumber, seatType, fare) => {
    const { selectedSeats } = get();
    const existing = selectedSeats.find(s => s.seatNumber === seatNumber);
    
    if (existing) {
      set({ selectedSeats: selectedSeats.filter(s => s.seatNumber !== seatNumber) });
    } else {
      if (selectedSeats.length >= 6) return; // Max 6 seats
      set({ selectedSeats: [...selectedSeats, { seatNumber, seatType, fare }] });
    }
  },
  
  clearSeats: () => set({ selectedSeats: [] }),
  
  setPassengers: (passengers) => set({ passengers }),
  setContactInfo: (info) => set({ contactInfo: info }),
  
  calculatePricing: () => {
    const { selectedSeats, discount } = get();
    const baseFare = selectedSeats.reduce((sum, s) => sum + s.fare, 0);
    const discountedAmount = baseFare - discount;
    const gst = Math.round(discountedAmount * 0.05 * 100) / 100;
    const totalAmount = Math.round((discountedAmount + gst) * 100) / 100;
    
    set({ baseFare, gst, totalAmount });
  },
  
  applyCoupon: (code, discountAmount) => {
    set({ couponCode: code, discount: discountAmount, couponApplied: true });
    get().calculatePricing();
  },
  
  removeCoupon: () => {
    set({ couponCode: '', discount: 0, couponApplied: false });
    get().calculatePricing();
  },
  
  setCurrentBooking: (booking) => set({ currentBooking: booking }),
  
  // Reset entire booking flow
  resetBooking: () => set({
    selectedSchedule: null,
    seatLayout: null,
    selectedSeats: [],
    passengers: [],
    contactInfo: { email: '', phone: '' },
    baseFare: 0,
    discount: 0,
    gst: 0,
    totalAmount: 0,
    couponCode: '',
    couponApplied: false,
    currentBooking: null,
  }),
}));

export default useBookingStore;
