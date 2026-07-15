import React, { useEffect, useMemo, useState } from "react";
import SeatMap from "./SeatMap";
import BoardingDropSelector from "./BoardingDropSelector";
import PassengerForm from "./PassengerForm";
import FareSummary from "./FareSummary";
import UpiPayment from "./UpiPayment";
import { BusApi, BookingApi } from "../api/api";
import "./BookingWizard.css";

// The checkout flow is modeled as an explicit state machine so the UI can
// never be in an ambiguous state: each STEP owns exactly one screen and one
// "can I move forward" rule.
const STEPS = {
  SEATS: "SEATS",
  BOARDING_DROP: "BOARDING_DROP",
  PASSENGER_DETAILS: "PASSENGER_DETAILS",
  FARE_SUMMARY: "FARE_SUMMARY",
  UPI_PAYMENT: "UPI_PAYMENT",
  CONFIRMED: "CONFIRMED",
};

const STEP_ORDER = [
  STEPS.SEATS,
  STEPS.BOARDING_DROP,
  STEPS.PASSENGER_DETAILS,
  STEPS.FARE_SUMMARY,
  STEPS.UPI_PAYMENT,
];

const STEP_LABELS = {
  [STEPS.SEATS]: "Seats",
  [STEPS.BOARDING_DROP]: "Points",
  [STEPS.PASSENGER_DETAILS]: "Passengers",
  [STEPS.FARE_SUMMARY]: "Summary",
  [STEPS.UPI_PAYMENT]: "Payment",
};

export default function BookingWizard({ tripId, userId, tripHeader }) {
  const [step, setStep] = useState(STEPS.SEATS);

  const [seats, setSeats] = useState([]);
  const [points, setPoints] = useState([]);
  const [loadError, setLoadError] = useState(null);

  const [selectedSeatIds, setSelectedSeatIds] = useState([]);
  const [boardingId, setBoardingId] = useState(null);
  const [droppingId, setDroppingId] = useState(null);
  const [passengers, setPassengers] = useState({});
  const [contact, setContact] = useState({ phone: "", email: "" });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [paymentPayload, setPaymentPayload] = useState(null); // { bookingId, upiUri, totalAmount, paymentWindowSeconds }

  useEffect(() => {
    async function loadTripData() {
      try {
        const [seatData, pointData] = await Promise.all([
          BusApi.getSeatLayout(tripId),
          BusApi.getTripPoints(tripId),
        ]);
        setSeats(seatData);
        setPoints(pointData);
      } catch (err) {
        setLoadError("Couldn't load seat layout. Please refresh and try again.");
      }
    }
    loadTripData();
  }, [tripId]);

  const selectedSeats = useMemo(
    () => seats.filter((s) => selectedSeatIds.includes(s.seatId)),
    [seats, selectedSeatIds]
  );

  const boardingPoint = points.find((p) => p.tripPointId === boardingId);
  const droppingPoint = points.find((p) => p.tripPointId === droppingId);

  // ---- per-step validation gates ----
  const canProceed = {
    [STEPS.SEATS]: selectedSeatIds.length > 0,
    [STEPS.BOARDING_DROP]: Boolean(boardingId && droppingId),
    [STEPS.PASSENGER_DETAILS]:
      selectedSeats.every((s) => {
        const p = passengers[s.seatId];
        return p && p.passengerName.trim() && p.age;
      }) && /^\d{10}$/.test(contact.phone) && /\S+@\S+\.\S+/.test(contact.email),
  }[step];

  const goNext = () => {
    const idx = STEP_ORDER.indexOf(step);
    if (idx < STEP_ORDER.length - 1) setStep(STEP_ORDER[idx + 1]);
  };
  const goBack = () => {
    const idx = STEP_ORDER.indexOf(step);
    if (idx > 0) setStep(STEP_ORDER[idx - 1]);
  };

  const toggleSeat = (seatId) => {
    setSelectedSeatIds((prev) =>
      prev.includes(seatId) ? prev.filter((id) => id !== seatId) : [...prev, seatId]
    );
  };

  const handleInitiateBooking = async () => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const payload = {
        userId,
        tripId,
        boardingTripPointId: boardingId,
        droppingTripPointId: droppingId,
        contactPhone: contact.phone,
        contactEmail: contact.email,
        passengers: selectedSeats.map((s) => ({
          seatId: s.seatId,
          passengerName: passengers[s.seatId].passengerName,
          age: Number(passengers[s.seatId].age),
          gender: passengers[s.seatId].gender,
        })),
      };

      const response = await BookingApi.initiate(payload);
      setPaymentPayload(response);
      setStep(STEPS.UPI_PAYMENT);
    } catch (err) {
      setSubmitError(
        err.response?.data?.message || "Couldn't start the booking. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePaymentConfirmed = () => setStep(STEPS.CONFIRMED);
  const handlePaymentExpired = () => {
    // Seats were never decremented from availability until payment is confirmed,
    // so simply drop the pending payload and let the user retry from Fare Summary.
    setPaymentPayload(null);
  };

  if (loadError) return <div className="status-banner status-banner--danger">{loadError}</div>;

  return (
    <div className="booking-wizard">
      <header className="booking-wizard__header">
        {tripHeader && (
          <div className="trip-header">
            <span className="trip-header__route">
              {tripHeader.sourceCity} → {tripHeader.destinationCity}
            </span>
            <span className="trip-header__operator">{tripHeader.operatorName}</span>
          </div>
        )}

        <ol className="step-tracker">
          {STEP_ORDER.map((s, i) => (
            <li
              key={s}
              className={`step-tracker__item ${
                s === step ? "step-tracker__item--active" : ""
              } ${STEP_ORDER.indexOf(step) > i ? "step-tracker__item--done" : ""}`}
            >
              <span className="step-tracker__dot">{i + 1}</span>
              <span className="step-tracker__label">{STEP_LABELS[s]}</span>
            </li>
          ))}
        </ol>
      </header>

      <div className="booking-wizard__body">
        {step === STEPS.SEATS && (
          <SeatMap seats={seats} selectedSeatIds={selectedSeatIds} onToggleSeat={toggleSeat} />
        )}

        {step === STEPS.BOARDING_DROP && (
          <BoardingDropSelector
            points={points}
            boardingId={boardingId}
            droppingId={droppingId}
            onSelectBoarding={setBoardingId}
            onSelectDropping={setDroppingId}
          />
        )}

        {step === STEPS.PASSENGER_DETAILS && (
          <PassengerForm
            seats={selectedSeats}
            passengers={passengers}
            onPassengerChange={(seatId, value) =>
              setPassengers((prev) => ({ ...prev, [seatId]: value }))
            }
            contact={contact}
            onContactChange={setContact}
          />
        )}

        {step === STEPS.FARE_SUMMARY && (
          <>
            <FareSummary
              seats={selectedSeats}
              boardingPoint={boardingPoint}
              droppingPoint={droppingPoint}
              onProceed={handleInitiateBooking}
              isSubmitting={isSubmitting}
            />
            {submitError && <div className="status-banner status-banner--danger">{submitError}</div>}
          </>
        )}

        {step === STEPS.UPI_PAYMENT && paymentPayload && (
          <UpiPayment
            bookingId={paymentPayload.bookingId}
            upiUri={paymentPayload.upiUri}
            amount={paymentPayload.totalAmount}
            paymentWindowSeconds={paymentPayload.paymentWindowSeconds}
            onConfirmed={handlePaymentConfirmed}
            onExpired={handlePaymentExpired}
          />
        )}

        {step === STEPS.CONFIRMED && (
          <div className="status-banner status-banner--success">
            🎉 Booking #{paymentPayload?.bookingId} confirmed. A copy of your ticket has been sent to{" "}
            {contact.email}.
          </div>
        )}
      </div>

      {step !== STEPS.CONFIRMED && step !== STEPS.UPI_PAYMENT && (
        <footer className="booking-wizard__footer">
          <button className="btn btn--ghost" onClick={goBack} disabled={step === STEPS.SEATS}>
            Back
          </button>
          {step !== STEPS.FARE_SUMMARY && (
            <button className="btn btn--primary" onClick={goNext} disabled={!canProceed}>
              Next
            </button>
          )}
        </footer>
      )}
    </div>
  );
}
