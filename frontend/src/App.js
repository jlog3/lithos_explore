import React, { useState } from 'react';
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

  return (
    <div className="app">
      <header>
        <h1>LithosCipher Explorer</h1>
      </header>
      <LocationInput 
        seed={seed} setSeed={setSeed}
        xOffset={xOffset} setXOffset={setXOffset}
        yOffset={yOffset} setYOffset={setYOffset}
        zOffset={zOffset} setZOffset={setZOffset}
        size={size} setSize={setSize}
      />
      <Explorer3D 
        seed={seed}
        xOffset={xOffset}
        yOffset={yOffset}
        zOffset={zOffset}
        size={size}
      />
      <EducationPanel />
    </div>
  );
}

export default App;
