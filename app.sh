#!/bin/bash

# Display banner
echo "=============================================="
echo "       Starting FlashAI Application          "
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in the PATH"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in the PATH"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed or not in the PATH"
    exit 1
fi

# Function to handle cleanup
cleanup() {
    echo "Shutting down FlashAI..."
    # Kill the backend process
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    # Kill the frontend process
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Setup trap for SIGINT (Ctrl+C)
trap cleanup SIGINT

# Check if .env file exists in root directory
if [ ! -f "./.env" ]; then
    # Create .env file with placeholder for API key
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=your_api_key_here" > ./.env
    echo "Please update the API key in .env file"
fi

# Install backend dependencies if needed
echo "Checking backend dependencies..."
if [ ! -d "./backend/venv" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv backend/venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source backend/venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi
pip install -r backend/requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install backend dependencies"
    exit 1
fi
pip install aiohttp  # Ensure aiohttp is installed for API calls

# Install frontend dependencies if needed
echo "Checking frontend dependencies..."
if [ ! -d "./frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install frontend dependencies"
        cd ..
        exit 1
    fi
    cd ..
fi

# Kill any process running on port 3000 (frontend)
echo "Checking if port 3000 is in use..."
PORT_PID=$(lsof -t -i:3000 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo "Killing process using port 3000..."
    kill -9 $PORT_PID 2>/dev/null
    sleep 1
fi

# Kill any process running on port 8000 (backend)
echo "Checking if port 8000 is in use..."
BACKEND_PORT_PID=$(lsof -t -i:8000 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo "Killing process using port 8000..."
    kill -9 $BACKEND_PORT_PID 2>/dev/null
    sleep 1
fi

# Create .env.local file for frontend to ensure it uses port 3000
echo "Configuring frontend port..."
echo "PORT=3000" > ./frontend/.env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" >> ./frontend/.env.local

echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for the backend to start and check if it's running
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running on port 8000
echo "Checking if backend is running..."
if ! lsof -i:8000 >/dev/null 2>&1; then
    echo "Warning: Backend may not have started properly"
    echo "Please check for errors above"
    sleep 3
fi

echo "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "FlashAI is running!"
echo "Backend server is available at http://localhost:8000"
echo "Frontend server is available at http://localhost:3000"
echo "Press Ctrl+C to stop both servers."

# Wait for backend process to finish (this will wait forever until Ctrl+C)
wait $BACKEND_PID