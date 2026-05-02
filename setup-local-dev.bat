@echo off
REM Insurance ChatBot - Local Development Setup for Windows

echo ================================================
echo Insurance ChatBot - Local Development Setup
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Python version: 
python --version
echo Node.js version: 
node --version
echo.

REM Setup Backend
echo ================================================
echo Setting up Backend...
echo ================================================
cd backend

REM Create virtual environment
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing backend dependencies...
pip install -r requirements.txt

REM Go back to root
cd ..

REM Setup Frontend
echo.
echo ================================================
echo Setting up Frontend...
echo ================================================
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

cd ..

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Install and start services (choose one method):
echo.
echo    Option A: Using Docker Compose (recommended for production)
echo    - Install Docker Desktop: https://www.docker.com/products/docker-desktop
echo    - Run: docker compose up -d
echo.
echo    Option B: Local Development (all services on same machine)
echo    - This is good for development
echo.
echo 2. For LOCAL development, you need to start these services separately:
echo.
echo    a) Start Ollama (LLM):
echo       - Download Ollama from https://ollama.ai/
echo       - Install and run it
echo       - Open new terminal and pull model: ollama pull mistral
echo       - Ollama will run on http://localhost:11434
echo.
echo    b) Start Redis (in another terminal):
echo       - Option 1: Run with Docker: docker run -p 6379:6379 redis:7-alpine
echo       - Option 2: Install Redis locally and run: redis-server
echo       - Redis will run on localhost:6379
echo.
echo    c) Start Backend (in another terminal):
echo       - cd backend
echo       - .venv\Scripts\activate.bat
echo       - uvicorn app.main:app --reload --port 8000
echo       - Backend will run on http://localhost:8000
echo.
echo    d) Start Ingest Service (in another terminal):
echo       - cd ingest_service
echo       - python -m venv .venv
echo       - .venv\Scripts\activate.bat
echo       - pip install -r requirements.txt
echo       - uvicorn app.main:app --reload --port 8001
echo       - Ingest will run on http://localhost:8001
echo.
echo    e) Start Frontend (in another terminal):
echo       - cd frontend
echo       - npm start
echo       - Frontend will run on http://localhost:4200
echo.
echo 3. Access the application:
echo    - Frontend: http://localhost:4200
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Default login: alice / AllianzTest123!
echo.
echo ================================================
pause
