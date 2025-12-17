import React from 'react';
function EducationPanel() {
  return (
    <div className="education-panel">
      <h2>About LithosCipher</h2>
      <p>This app uses cryptographic hashing to generate procedural rock formations.</p>
      <p>Each point in 3D space is determined by hashing the seed and coordinates, normalized to select a mineral based on probabilities.</p>
      <p>Minerals and Probabilities:</p>
      <p>Probabilities vary by mineral and depth layer for geologic realism, based on real data. See minerals.json for specific probabilities, minerals, and properties.</p>
      <p>Location inputs are hashed to generate unique offsets for region-specific exploration, simulating geographic variety. Real APIs (Nominatim/USGS) boost local minerals for accuracy.</p>
      <p>Depth Layers (simulating Earth's crust):</p>
      <p>Scale: Each voxel represents approximately 10m x 10m x 10m for realism. Note: This is simplified—a gold voxel isn't a pure 10m block but a region rich in gold ore.</p>
      <ul>
        <li>0-10 units (Surface): Felsic/sedimentary minerals with higher porosity.</li>
        <li>11-35 units (Crust): Transition/veins with ores and mafic elements.</li>
        <li>36+ units (Deep): Mafic/rares with diamonds and gems.</li>
      </ul>
      <p>For more: See <a href="https://en.wikipedia.org/wiki/Earth%27s_crust">Earth's Crust Composition</a>.</p>
    </div>
  );
}
export default EducationPanel;
