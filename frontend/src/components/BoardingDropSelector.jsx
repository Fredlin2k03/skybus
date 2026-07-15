import React from "react";

/**
 * points: [{ tripPointId, pointType: 'Boarding'|'Dropping', name, landmarkTime, address }]
 */
export default function BoardingDropSelector({ points, boardingId, droppingId, onSelectBoarding, onSelectDropping }) {
  const boardingPoints = points.filter((p) => p.pointType === "Boarding");
  const droppingPoints = points.filter((p) => p.pointType === "Dropping");

  const formatTime = (iso) =>
    new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const PointList = ({ list, selectedId, onSelect, heading }) => (
    <div className="point-group">
      <h3 className="point-group__heading">{heading}</h3>
      <div className="point-list">
        {list.map((p) => (
          <label key={p.tripPointId} className={`point-card ${selectedId === p.tripPointId ? "point-card--active" : ""}`}>
            <input
              type="radio"
              name={heading}
              checked={selectedId === p.tripPointId}
              onChange={() => onSelect(p.tripPointId)}
            />
            <div className="point-card__body">
              <span className="point-card__time">{formatTime(p.landmarkTime)}</span>
              <span className="point-card__name">{p.name}</span>
              {p.address && <span className="point-card__address">{p.address}</span>}
            </div>
          </label>
        ))}
      </div>
    </div>
  );

  return (
    <div className="boarding-drop">
      <PointList list={boardingPoints} selectedId={boardingId} onSelect={onSelectBoarding} heading="Boarding point" />
      <PointList list={droppingPoints} selectedId={droppingId} onSelect={onSelectDropping} heading="Dropping point" />
    </div>
  );
}
