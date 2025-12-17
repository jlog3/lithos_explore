#!/bin/bash

# Check if Conda is available
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

ENV_NAME="lithos_explore"

# Source Conda activation script (adjust path if your Conda install is elsewhere)
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Create env if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "Creating Conda env '$ENV_NAME' from environment.yaml..."
    conda env create -f environment.yaml
fi

# Activate the env
echo "Activating Conda env '$ENV_NAME'..."
conda activate $ENV_NAME

# Kill any processes on ports 5000 and 3000 (using fuser for reliability)
echo "Terminating any existing processes on ports 5000 and 3000..."
sudo fuser -k 5000/tcp 2>/dev/null || true
sudo fuser -k 3000/tcp 2>/dev/null || true

# Sort and copy minerals.json (run this before starting servers)
echo "Sorting and copying minerals.json..."
python scripts/sort_minerals_json.py

# Start backend in background
echo "Starting Flask backend..."
cd backend
pip install -r requirements.txt  # Ensures any extras are installed
python app.py &
BACKEND_PID=$!
cd ..

# Start frontend (auto-answer 'y' to port prompt)
echo "Starting React frontend..."
cd frontend
npm install
yes y | npm start &
FRONTEND_PID=$!
cd ..

# Wait for processes (Ctrl+C to stop)
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; conda deactivate" INT
wait $BACKEND_PID $FRONTEND_PID
