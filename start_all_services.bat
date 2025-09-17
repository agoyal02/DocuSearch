@echo off
REM DocuSearch - Complete Service Startup Script for Windows
REM This script starts all required services for the DocuSearch application

setlocal enabledelayedexpansion

REM Configuration
set APP_PORT=5000
set GROBID_PORT=8070
set GROBID_HEALTH_URL=http://localhost:%GROBID_PORT%/api/isalive
set APP_URL=http://localhost:%APP_PORT%

echo.
echo 🚀 DocuSearch Service Manager
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  pip not found. Attempting to install pip...
    
    REM Try to install pip using get-pip.py
    if exist "get-pip.py" (
        echo 📥 Using local get-pip.py to install pip...
        python get-pip.py --user
    ) else (
        echo 📥 Downloading get-pip.py...
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
        if errorlevel 1 (
            echo ❌ Failed to download get-pip.py
            echo Please install pip manually from: https://pip.pypa.io/en/stable/installation/
            pause
            exit /b 1
        )
        python get-pip.py --user
        del get-pip.py
    )
    
    REM Add user Scripts to PATH
    for /f "tokens=2*" %%i in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set USER_PATH=%%j
    if not defined USER_PATH set USER_PATH=%USERPROFILE%\AppData\Roaming\Python\Python39\Scripts;%USERPROFILE%\AppData\Roaming\Python\Python310\Scripts;%USERPROFILE%\AppData\Roaming\Python\Python311\Scripts;%USERPROFILE%\AppData\Roaming\Python\Python312\Scripts
    set PATH=%USER_PATH%;%PATH%
    
    REM Verify pip installation
    pip --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ pip installation failed
        echo Please install pip manually from: https://pip.pypa.io/en/stable/installation/
        pause
        exit /b 1
    ) else (
        echo ✅ pip installed successfully
    )
) else (
    echo ✅ pip is already installed
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker not found. Attempting to install Docker Desktop...
    
    REM Check if Chocolatey is available
    choco --version >nul 2>&1
    if not errorlevel 1 (
        echo 📥 Installing Docker Desktop using Chocolatey...
        choco install docker-desktop -y
        if errorlevel 1 (
            echo ❌ Docker Desktop installation failed via Chocolatey
            goto :manual_docker_install
        )
    ) else (
        REM Check if winget is available
        winget --version >nul 2>&1
        if not errorlevel 1 (
            echo 📥 Installing Docker Desktop using winget...
            winget install Docker.DockerDesktop
            if errorlevel 1 (
                echo ❌ Docker Desktop installation failed via winget
                goto :manual_docker_install
            )
        ) else (
            goto :manual_docker_install
        )
    )
    
    echo ✅ Docker Desktop installed successfully
    echo ⚠️  Please start Docker Desktop manually and run this script again
    pause
    exit /b 0
    
    :manual_docker_install
    echo ❌ Automatic Docker installation failed.
    echo Please install Docker Desktop manually from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
) else (
    echo ✅ Docker is already installed
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  docker-compose not found. Attempting to install...
    
    REM Try to install docker-compose via pip
    pip install docker-compose
    if errorlevel 1 (
        echo ❌ docker-compose installation failed
        echo Please install Docker Compose manually from: https://github.com/docker/compose/releases
        pause
        exit /b 1
    ) else (
        echo ✅ docker-compose installed successfully
    )
) else (
    echo ✅ docker-compose is already available
)

echo 📁 Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "parsed_documents" mkdir parsed_documents
if not exist "job_results" mkdir job_results
if not exist "job_metadata" mkdir job_metadata
if not exist "schemas" mkdir schemas

echo 📦 Setting up Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📥 Installing Python dependencies...
    pip install -r requirements.txt
) else (
    echo ✅ Python dependencies are already installed
)

echo 🔬 Starting GROBID service...
docker-compose up -d grobid

echo ⏳ Waiting for GROBID to be ready...
timeout /t 30 /nobreak >nul

REM Check if GROBID is running
curl -f %GROBID_HEALTH_URL% >nul 2>&1
if errorlevel 1 (
    echo ❌ GROBID failed to start. Check the logs with: docker-compose logs grobid
    pause
    exit /b 1
) else (
    echo ✅ GROBID is running and ready!
)

echo 🌐 Starting DocuSearch application...
start /b python app.py > app.log 2>&1

REM Wait a moment for the app to start
timeout /t 5 /nobreak >nul

REM Check if the application is running
curl -f %APP_URL% >nul 2>&1
if errorlevel 1 (
    echo ❌ DocuSearch application failed to start. Check app.log for details.
    pause
    exit /b 1
) else (
    echo ✅ DocuSearch application started successfully!
)

echo.
echo 🎉 DocuSearch is now running!
echo ==============================
echo 🌐 Web Interface: %APP_URL%
echo 📊 Metrics: %APP_URL%/metrics
echo 🔍 Search API: %APP_URL%/search?q=your_query
echo 📁 Upload API: %APP_URL%/upload
echo 📦 Bulk Upload: %APP_URL%/bulk_upload
echo ☁️  S3 Upload: %APP_URL%/bulk_upload_s3
echo.
echo 📝 Application logs: type app.log
echo 🛑 To stop: docker-compose down ^&^& taskkill /f /im python.exe
echo.
echo Press any key to continue...
pause >nul
