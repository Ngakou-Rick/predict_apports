#!/bin/bash

# Start Backend
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Frontend
cd frontend && npm start -- -p 3000 &
FRONTEND_PID=$!

echo "Backend running on port 8000 (PID $BACKEND_PID)"
echo "Frontend running on port 3000 (PID $FRONTEND_PID)"

wait
