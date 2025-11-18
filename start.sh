#!/bin/bash

# Check if Conda is available
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

ENV_NAME="lithos_explore"

# Create env if it doesn't exist
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "Creating Conda env '$ENV_NAME' from environment.yaml..."
    conda env create -f environment.yaml
fi

# Activate the env
echo "Activating Conda env '$ENV_NAME'..."
conda activate $ENV_NAME

# Start backend in background
echo "Starting Flask backend..."
cd backend
pip install -r requirements.txt  # Ensures any extras are installed
python app.py &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting React frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

# Wait for processes (Ctrl+C to stop)
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; conda deactivate" INT
wait $BACKEND_PID $FRONTEND_PID
