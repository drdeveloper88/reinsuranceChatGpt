@echo off
REM Insurance ChatBot - Quick Start Script for Windows

echo ================================================
echo Insurance ChatBot - Quick Start
echo ================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Prefer Docker Compose V2 plugin (fallback to docker-compose v1)
docker compose version >nul 2>&1
set USE_LEGACY_COMPOSE=0
if %errorlevel% neq 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Docker Compose not found. Install Docker Desktop ^(includes compose v2^).
        pause
        exit /b 1
    )
    set USE_LEGACY_COMPOSE=1
)

REM Copy environment files if they don't exist
if not exist "backend\.env" (
    echo Creating backend .env file...
    copy backend\.env.example backend\.env
)

if not exist "ingest_service\.env" (
    echo Creating ingest service .env file...
    copy ingest_service\.env.example ingest_service\.env
)

echo.
echo Starting services...
echo This may take a few minutes on first run...
echo.

REM Start services
if "%USE_LEGACY_COMPOSE%"=="1" (
    docker-compose up -d
) else (
    docker compose up -d
)

REM Wait for services to be ready
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak

REM Check service health
echo.
echo Checking service health...

REM Check backend
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend API is running (http://localhost:8000)
) else (
    echo ✗ Backend API not responding yet, giving it more time...
    timeout /t 5 /nobreak
)

REM Check ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Ollama LLM is running (http://localhost:11434)
) else (
    echo ✗ Ollama not responding yet
)

echo.
echo ================================================
echo Services are starting up!
echo ================================================
echo.
echo Access the application at:
echo   Frontend:         http://localhost:4200
echo   Backend API:      http://localhost:8000
echo   API Docs:         http://localhost:8000/docs
echo   Ingest Service:   http://localhost:8001
echo   Redis:            localhost:6379
echo   Ollama:           http://localhost:11434
echo.
echo Useful commands:
echo   View logs:        docker compose logs -f backend
echo   Stop services:    docker compose down
echo   Rebuild images:   docker compose up --build
echo.
echo Default login credentials:
echo   Username: alice
echo   Password: AllianzTest123!
echo.
echo First run note: Ollama may take a minute to download the model.
echo Check logs: docker compose logs -f ollama
echo.
echo ================================================
pause
