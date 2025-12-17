import React, { useState } from 'react';
import MapSelector from './MapSelector'; // Import the map

function LocationInput({ seed, setSeed, xOffset, setXOffset, yOffset, setYOffset, zOffset, setZOffset, size, setSize, probOffsets, setProbOffsets, crustType, setCrustType, chunkX, setChunkX, chunkY, setChunkY, chunkZ, setChunkZ, testMode, setTestMode, selectedMinerals, setSelectedMinerals, mineralColors }) {
  const [location, setLocation] = useState('');
  const [message, setMessage] = useState('');
  const [debugData, setDebugData] = useState(null);

  const handleLocationSubmit = async (e) => {
    if (e) e.preventDefault(); // Allow programmatic calls without event
    if (!location) return;
    try {
      const response = await fetch(`/api/offsets?location=${encodeURIComponent(location)}&debug=true`);
      if (response.ok) {
        const data = await response.json();
        setXOffset(data.x_offset);
        setYOffset(data.y_offset);
        setZOffset(data.z_offset);
        setCrustType(data.crust_type);
        setProbOffsets(data.prob_offsets);
        const boosts = Object.keys(data.prob_offsets).length ? JSON.stringify(data.prob_offsets) : 'None';
        setMessage(`Success: Fetched offsets for ${location}. Crust: ${data.crust_type}. Boosts applied: ${boosts}`);
        setDebugData(data.debug_info || null);
        console.log("Success: Location offsets fetched.", data);
      } else {
        setMessage(`Failure: Error fetching offsets (status ${response.status})`);
        console.error("Failure: Error fetching offsets", response.status);
      }
    } catch (error) {
      setMessage(`Failure: Fetch error - ${error.message}`);
      console.error("Failure: Fetch error", error);
    }
  };

  // Handler for map clicks
  const handleMapClick = (lat, lon) => {
    const newLocation = `${lat},${lon}`;
    setLocation(newLocation);
    handleLocationSubmit(); // Auto-submit to fetch offsets immediately
  };

  const toggleMineral = (mineral) => {
    setSelectedMinerals(prev =>
      prev.includes(mineral) ? prev.filter(m => m !== mineral) : [...prev, mineral]
    );
  };

  const downloadJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="location-input">
      {/* Add the map */}
      <h3>Click on the Map to Select Location</h3>
      <MapSelector onLocationSelect={handleMapClick} />
      <form onSubmit={handleLocationSubmit}>
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter location (e.g., Paris or 37.7749,-122.4194)"
        />
        <button type="submit">Go to Location</button>
        <button onClick={() => setZOffset(Math.max(0, zOffset - 10))}>Ascend (-10)</button>
        <button onClick={() => setZOffset(zOffset + 10)}>Dig Deeper (+10)</button>
        <button onClick={() => setChunkX(chunkX + 1)}>Expand X (+)</button>
        <button onClick={() => setChunkX(chunkX - 1)}>Expand X (-)</button>
        <button onClick={() => setChunkY(chunkY + 1)}>Expand Y (+)</button>
        <button onClick={() => setChunkY(chunkY - 1)}>Expand Y (-)</button>
        <button onClick={() => setChunkZ(chunkZ + 1)}>Expand Z (+)</button>
        <button onClick={() => setChunkZ(chunkZ - 1)}>Expand Z (-)</button>
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
        <input type="number" value={size} onChange={(e) => setSize(Math.min(Math.max(parseInt(e.target.value) || 32, 1), 128))} min="1" max="128" />
      </div>
      <div>
        <label>Test Mode:
          <input
            type="checkbox"
            checked={testMode}
            onChange={(e) => setTestMode(e.target.checked)}
          />
        </label>
      </div>
      {testMode && (
        <div>
          <h3>Select Minerals for World Generation</h3>
          {Object.keys(mineralColors)
            .filter(min => min !== 'void' && min !== 'cover')
            .map(min => (
              <label key={min}>
                <input
                  type="checkbox"
                  checked={selectedMinerals.includes(min)}
                  onChange={() => toggleMineral(min)}
                />
                {min.charAt(0).toUpperCase() + min.slice(1)}
              </label>
            ))}
        </div>
      )}
      {debugData && (
        <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
          <h3>Debug Data for {debugData.location}</h3>
          <pre>{JSON.stringify(debugData, null, 2)}</pre>
          <button onClick={() => downloadJSON(debugData, 'debug_data.json')}>
            Download Debug JSON
          </button>
        </div>
      )}
      <p>Crust Type: {crustType}</p>
      <p style={{ color: message.startsWith('Success') ? 'green' : 'red' }}>{message}</p>
    </div>
  );
}

export default LocationInput;
