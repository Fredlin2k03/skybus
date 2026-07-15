import axios from "axios";

// Phase 1: local .NET API on port 5001 talking directly to Azure SQL.
// Phase 2: this becomes the App Service URL, fronted by App Gateway.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "https://localhost:5001/api";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("bb_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const AuthApi = {
  register: (payload) => client.post("/auth/register", payload).then((r) => r.data),
  login: (payload) => client.post("/auth/login", payload).then((r) => r.data),
};

export const BusApi = {
  search: (source, destination, date) =>
    client.get("/bus/search", { params: { source, destination, date } }).then((r) => r.data),
  getSeatLayout: (tripId) =>
    client.get(`/bus/trip/${tripId}/seats`).then((r) => r.data),
  getTripPoints: (tripId) =>
    client.get(`/bus/trip/${tripId}/points`).then((r) => r.data),
};

export const BookingApi = {
  initiate: (payload) => client.post("/booking/initiate", payload).then((r) => r.data),
  confirmPayment: (bookingId, upiTransactionRef) =>
    client.post(`/booking/${bookingId}/confirm-payment`, { upiTransactionRef }).then((r) => r.data),
  getById: (bookingId) => client.get(`/booking/${bookingId}`).then((r) => r.data),
  cancel: (bookingId) => client.post(`/booking/${bookingId}/cancel`).then((r) => r.data),
};

export default client;
