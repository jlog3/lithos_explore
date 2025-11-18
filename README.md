# LithosCipher Explorer
Web app for exploring procedural rocks.

## Prerequisites
- [Miniconda or Anaconda](https://docs.conda.io/en/latest/miniconda.html) for Python environment management.
- Node.js (v14+) and npm/yarn for the frontend (install via https://nodejs.org/).

## Setup and Run
1. Clone the repo:
git clone <your-repo-url>
cd lithos_explore


2. Run the startup script—it handles everything (creates/activates Conda env, installs deps, starts servers):
./start.sh

- Backend (Flask) runs on http://localhost:5000.
- Frontend (React) runs on http://localhost:3000 (proxies API calls to backend).

3. Open http://localhost:3000 in your browser. Enter a seed, location, or offsets to explore 3D regions.

## Manual Setup (if needed)
- Create/activate Conda env: `conda env create -f environment.yaml && conda activate lithos_explore`
- Backend: `cd backend && pip install -r requirements.txt && python app.py`
- Frontend (separate terminal): `cd frontend && npm install && npm start`

## Features
- 3D chunk visualization with rotation/zoom using Three.js.
- User location input maps to offsets for "geographic" exploration (via hashing).
- Educational explanations of hashing.
- API for mineral queries, 2D slices, and 3D chunks.
- Region-specific: Enter a location string to jump to a unique offset-based view.

## Notes
- For production, use a proxy like nginx to serve both.
- Optimize 3D rendering for larger sizes if needed.
- If CORS issues arise, add `from flask_cors import CORS` to `backend/app.py`, then `CORS(app)` after `app = Flask(__name__)`.
- To stop: Ctrl+C in the terminal running `start.sh`.
