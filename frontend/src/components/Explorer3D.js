import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Box } from '@react-three/drei';

const MINERAL_COLORS = {
  'void': 'white',
  'quartz': 'gray',
  'feldspar': 'pink',
  'mica': 'black',
  'gold': 'yellow'
};

function Voxels({ chunk }) {
  if (!chunk || chunk.length === 0) return null;
  const voxels = [];
  chunk.forEach((plane, x) => {
    plane.forEach((row, y) => {
      row.forEach((mineral, z) => {
        if (mineral !== 'void') {  // Skip voids for better performance
          voxels.push(
            <Box key={`${x}-${y}-${z}`} position={[x, y, z]} args={[1, 1, 1]}>
              <meshStandardMaterial color={MINERAL_COLORS[mineral]} />
            </Box>
          );
        }
      });
    });
  });
  return <group>{voxels}</group>;
}

function Explorer3D({ seed, xOffset, yOffset, zOffset, size }) {
  const [chunk, setChunk] = useState([]);

  useEffect(() => {
    const fetchChunk = async () => {
      const params = new URLSearchParams({
        seed,
        size,
        x_offset: xOffset,
        y_offset: yOffset,
        z_offset: zOffset
      });
      try {
        const response = await fetch(`/api/chunk3d?${params.toString()}`);
        if (response.ok) {
          const data = await response.json();
          setChunk(data);
        } else {
          console.error('Error fetching chunk');
        }
      } catch (error) {
        console.error('Fetch error:', error);
      }
    };
    fetchChunk();
  }, [seed, xOffset, yOffset, zOffset, size]);

  return (
    <div className="explorer-3d">
      <Canvas camera={{ position: [size / 2, size / 2, size * 1.5] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[size, size, size]} />
        <Voxels chunk={chunk} />
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default Explorer3D;
