import React, { useState } from 'react';

function LocationInput({ seed, setSeed, xOffset, setXOffset, yOffset, setYOffset, zOffset, setZOffset, size, setSize }) {
  const [location, setLocation] = useState('');

  const handleLocationSubmit = async (e) => {
    e.preventDefault();
    if (!location) return;
    try {
      const response = await fetch(`/api/offsets?location=${encodeURIComponent(location)}`);
      if (response.ok) {
        const data = await response.json();
        setXOffset(data.x_offset);
        setYOffset(data.y_offset);
        setZOffset(data.z_offset);
      } else {
        console.error('Error fetching offsets');
      }
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  return (
    <div className="location-input">
      <form onSubmit={handleLocationSubmit}>
        <input 
          type="text" 
          value={location} 
          onChange={(e) => setLocation(e.target.value)} 
          placeholder="Enter location (e.g., Paris)" 
        />
        <button type="submit">Go to Location</button>
      </form>
      <div>
        <label>Seed:</label>
        <input type="text" value={seed} onChange={(e) => setSeed(e.target.value)} />
      </div>
      <div>
        <label>X Offset:</label>
        <input type="number" value={xOffset} onChange={(e) => setXOffset(parseInt(e.target.value) || 0)} />
      </div>
      <div>
        <label>Y Offset:</label>
        <input type="number" value={yOffset} onChange={(e) => setYOffset(parseInt(e.target.value) || 0)} />
      </div>
      <div>
        <label>Z Offset:</label>
        <input type="number" value={zOffset} onChange={(e) => setZOffset(parseInt(e.target.value) || 0)} />
      </div>
      <div>
        <label>Size:</label>
        <input type="number" value={size} onChange={(e) => setSize(parseInt(e.target.value) || 32)} min="1" />
      </div>
    </div>
  );
}

export default LocationInput;
