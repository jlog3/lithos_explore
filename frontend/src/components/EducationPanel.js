import React from 'react';

function EducationPanel() {
  return (
    <div className="education-panel">
      <h2>About LithosCipher</h2>
      <p>This app uses cryptographic hashing to generate procedural rock formations.</p>
      <p>Each point in 3D space is determined by hashing the seed and coordinates, normalized to select a mineral based on probabilities.</p>
      <p>Minerals and Probabilities:</p>
      <ul>
        <li>Void (40%): white (empty space for porosity)</li>
        <li>Quartz (30%): gray (common)</li>
        <li>Feldspar (15%): pink</li>
        <li>Mica (10%): black</li>
        <li>Gold (5%): yellow (rare veins)</li>
      </ul>
      <p>Location inputs are hashed to generate unique offsets for region-specific exploration, simulating geographic variety.</p>
    </div>
  );
}

export default EducationPanel;
