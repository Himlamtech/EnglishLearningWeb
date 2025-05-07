@echo off
cls
echo ==============================================
echo        Starting FlashAI Application
echo ==============================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in the PATH
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Node.js is not installed or not in the PATH
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm is not installed or not in the PATH
    exit /b 1
)

REM Check if .env file exists in root directory
if not exist ".env" (
    echo Creating .env file...
    echo OPENAI_API_KEY=your_api_key_here > .env
    echo Please update the API key in .env file
)

REM Install backend dependencies if needed
echo Checking backend dependencies...
if not exist "backend\venv" (
    echo Setting up Python virtual environment...
    python -m venv backend\venv
)

REM Activate virtual environment and install dependencies
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt
pip install aiohttp

REM Install frontend dependencies if needed
echo Checking frontend dependencies...
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    cd ..
)

REM Kill any process running on port 3000
echo Checking if port 3000 is in use...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing process using port 3000...
    taskkill /F /PID %%a 2>nul
    timeout /t 1 /nobreak > nul
)

REM Create .env.local file for frontend to ensure it uses port 3000
echo Configuring frontend port...
echo PORT=3000> frontend\.env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000>> frontend\.env.local

REM Start servers in separate command windows
echo Starting backend server...
start "FlashAI Backend" cmd /c "cd backend && call venv\Scripts\activate.bat && python run.py"

REM Wait a bit for the backend to start
timeout /t 3 /nobreak > nul

echo Starting frontend development server...
start "FlashAI Frontend" cmd /c "cd frontend && npm run dev"

echo FlashAI is running!
echo Backend server is available at http://localhost:8000
echo Frontend server is available at http://localhost:3000
echo Close the command windows to stop the servers.

REM Keep the main window open
pause