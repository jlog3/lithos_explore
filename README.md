# Lithos Explorer
Web app (Flask, React) for exploring geologically representative 3D rock formations using real-world data.

## Overview
This project integrates real geologic data from APIs to generate 3D rock chunks that approximate actual compositions for user-entered locations. It geocodes locations, fetches stratigraphic and lithologic data (e.g., via Macrostrat API), and adjusts procedural generation accordingly—mapping real rock types to minerals, probabilities, and layers. It's educational, focusing on real geology while retaining some procedural elements for visualization.
Stack:
- Backend: Python 3.10 with Flask for API, requests for external APIs, hashlib for offsets, NumPy for array ops.
- Frontend: React with React Three Fiber (@react-three/fiber, @react-three/drei) for 3D rendering using Three.js.
- Environment: Managed via Conda (environment.yaml) and pip (requirements.txt, including requests).
- Other: CORS for cross-origin requests, proxy setup in package.json for dev; external APIs: geocode.maps.co (geocoding), Macrostrat (geology).

## Prerequisites
- [Miniconda or Anaconda](https://docs.conda.io/en/latest/miniconda.html) for Python environment management.
- Node.js (v14+) and npm/yarn for the frontend (install via https://nodejs.org/).

## Setup and Run
1. Clone the repo:
```bash
git clone https://github.com/jlog3/lithos_explore.git
cd lithos_explore
```

2. Run the startup script—it handles everything (creates/activates Conda env, installs deps, starts servers):
```bash
./start.sh
```
- Backend (Flask) runs on http://localhost:5000.
- Frontend (React) runs on http://localhost:3000 (proxies API calls to backend).

3. Open http://localhost:3000 in your browser. Enter a location to fetch real geologic data and explore adjusted 3D regions.

## Manual Setup (if needed)
- Create/activate Conda env: `conda env create -f environment.yaml && conda activate lithos_explore`
- Backend: `cd backend && pip install -r requirements.txt && python app.py`
- Frontend (separate terminal): `cd frontend && npm install && npm start`

## Features
- Real geologic data integration: Geocodes locations, fetches units/lithologies from Macrostrat, adjusts mineral probabilities/colors/layers.
- 3D visualization of stratified chunks based on real stratigraphic columns (e.g., vertical layers from thicknesses).
- Dynamic educational panel showing fetched data (e.g., rock types, ages, depths) and voxel scale (e.g., ~100 ft³ per voxel).
- Location-based exploration: Hashed offsets for procedural variety, overlaid with real compositions.
- API endpoints: Extended /api/offsets includes geology; /api/chunk3d adjusts based on data.
- Size/zoom controls with loading states and error handling.

## Notes
- This version emphasizes accuracy with real data—fallback to procedural if APIs fail.
- API usage: Free tiers (no keys needed), but respect rate limits; cache results in production.
- For production, deploy backend with Gunicorn/NGINX and build frontend statically (npm run build).
- Optimize for data-heavy fetches: Add caching (e.g., Redis) for repeated locations.
- If CORS issues: Already handled via flask-cors.
- To stop: Ctrl+C in the terminal running start.sh.
- Future ideas: Add more APIs (e.g., USGS for US-specific), interactive layer slicing, export reports.
- For adding textures to new (or old) minerals follow directions in docs/BLENDER_TEXTURE_GUIDE.md
	Place all PNGs in frontend/public/textures/  and update constants (textures in frontend/src/components/Explorer3D.js) and MINERAL_COLORS in app.py (frontend: color acts as a tint or multiplier on the texture enhancing realism—textures provide detail/pattern, colors provide hue/variation.; backend: In generate_slice, it fills a NumPy array with RGB colors for 2D slices (e.g., small_grid[y, x] = MINERAL_COLORS[mineral]).
	This is for potential 2D visualizations (e.g., exporting images or slices via /api/slice2d, which returns mineral strings but could be extended to colors).)
