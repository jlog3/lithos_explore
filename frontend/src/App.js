import React, { useState, useEffect } from 'react';
import Explorer3D from './components/Explorer3D';
import LocationInput from './components/LocationInput';
import EducationPanel from './components/EducationPanel';
import './styles.css';
function App() {
  const [seed, setSeed] = useState('default_seed');
  const [xOffset, setXOffset] = useState(0);
  const [yOffset, setYOffset] = useState(0);
  const [zOffset, setZOffset] = useState(0);
  const [size, setSize] = useState(32);
  const [currentDepth, setCurrentDepth] = useState(0);
  const [probOffsets, setProbOffsets] = useState({});
  const [crustType, setCrustType] = useState('');
  const [chunkX, setChunkX] = useState(0);
  const [chunkY, setChunkY] = useState(0);
  const [chunkZ, setChunkZ] = useState(0);
  const [testMode, setTestMode] = useState(false);
  const [selectedMinerals, setSelectedMinerals] = useState([]);
  const [mineralColors, setMineralColors] = useState({});
  useEffect(() => {
    const fetchMinerals = async () => {
      try {
        const response = await fetch('/minerals.json');
        if (response.ok) {
          const data = await response.json();
          const colors = {
            'void': [255, 255, 255],
            'cover': [165, 42, 42]
          };
          Object.entries(data.minerals).forEach(([name, minData]) => {
            colors[name] = minData.color;
          });
          data.coverVariants.forEach((variant) => {
            colors[`cover_${variant.id}`] = variant.color;
          });
          setMineralColors(colors);
        }
      } catch (error) {
        console.error('Error fetching minerals.json:', error);
      }
    };
    fetchMinerals();
  }, []);
  // Pass to LocationInput and Explorer3D as zOffset = currentDepth
  return (
    <div className="app">
      <header>
        <h1>LithosCipher Explorer</h1>
      </header>
      <LocationInput
        seed={seed} setSeed={setSeed}
        xOffset={xOffset} setXOffset={setXOffset}
        yOffset={yOffset} setYOffset={setYOffset}
        zOffset={currentDepth} setZOffset={setCurrentDepth}
        size={size} setSize={setSize}
        probOffsets={probOffsets} setProbOffsets={setProbOffsets}
        crustType={crustType} setCrustType={setCrustType}
        chunkX={chunkX} setChunkX={setChunkX}
        chunkY={chunkY} setChunkY={setChunkY}
        chunkZ={chunkZ} setChunkZ={setChunkZ}
        testMode={testMode} setTestMode={setTestMode}
        selectedMinerals={selectedMinerals} setSelectedMinerals={setSelectedMinerals}
        mineralColors={mineralColors}
      />
      <Explorer3D
        seed={seed}
        xOffset={xOffset}
        yOffset={yOffset}
        zOffset={currentDepth}
        size={size}
        probOffsets={probOffsets}
        chunkX={chunkX}
        chunkY={chunkY}
        chunkZ={chunkZ}
        testMode={testMode}
        selectedMinerals={selectedMinerals}
        mineralColors={mineralColors}
        crustType={crustType}  // Added for location-based cover variants
      />
      <EducationPanel />
    </div>
  );
}
export default App;
