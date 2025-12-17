import React from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';

function MapClickHandler({ onClick }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onClick(lat.toFixed(4), lng.toFixed(4)); // Round to 4 decimals for precision
    },
  });
  return null;
}

function MapSelector({ onLocationSelect }) {
  return (
    <MapContainer
      center={[0, 0]} // Center on equator/prime meridian
      zoom={2} // Global view
      style={{ height: '300px', width: '100%', marginBottom: '20px' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <MapClickHandler onClick={onLocationSelect} />
    </MapContainer>
  );
}

export default MapSelector;
