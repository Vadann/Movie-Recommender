#!/bin/bash

echo "========================================"
echo "   Movie Recommender - Quick Start"
echo "========================================"
echo ""

# Check if ML model exists
if [ ! -f "backend/app/ml/movie_data.pkl" ]; then
    echo "ML model not found. Running preprocessing..."
    cd backend
    source venv/bin/activate
    python -m app.ml.preprocessing
    cd ..
    echo ""
fi

# Start backend
echo "Starting Backend Server..."
cd backend
source venv/bin/activate
python -m app.main &
BACKEND_PID=$!
cd ..

sleep 3

# Start frontend
echo "Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait


