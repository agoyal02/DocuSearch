@echo off
REM DocuSearch - Docker Installation Script for Windows
REM This script installs Docker Desktop and docker-compose if they're not already available

setlocal enabledelayedexpansion

echo.
echo 🐳 DocuSearch Docker Installation
echo ==================================
echo.

REM Check if Docker is already installed
docker --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Docker is already installed
    docker --version
    set DOCKER_INSTALLED=true
) else (
    echo ⚠️  Docker not found. Installing Docker Desktop...
    set DOCKER_INSTALLED=false
)

REM Check if docker-compose is already installed
docker-compose --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ docker-compose is already installed
    docker-compose --version
    set COMPOSE_INSTALLED=true
) else (
    echo ⚠️  docker-compose not found. Installing docker-compose...
    set COMPOSE_INSTALLED=false
)

REM Install Docker if needed
if "%DOCKER_INSTALLED%"=="false" (
    echo 📥 Installing Docker Desktop...
    
    REM Check if Chocolatey is available
    choco --version >nul 2>&1
    if not errorlevel 1 (
        echo 📦 Using Chocolatey to install Docker Desktop...
        choco install docker-desktop -y
        if errorlevel 1 (
            echo ❌ Docker Desktop installation failed via Chocolatey
            goto :manual_docker_install
        )
        echo ✅ Docker Desktop installed via Chocolatey
    ) else (
        REM Check if winget is available
        winget --version >nul 2>&1
        if not errorlevel 1 (
            echo 📦 Using winget to install Docker Desktop...
            winget install Docker.DockerDesktop
            if errorlevel 1 (
                echo ❌ Docker Desktop installation failed via winget
                goto :manual_docker_install
            )
            echo ✅ Docker Desktop installed via winget
        ) else (
            goto :manual_docker_install
        )
    )
    
    echo ⚠️  Docker Desktop has been installed. Please start Docker Desktop manually.
    echo After starting Docker Desktop, run this script again to install docker-compose.
    pause
    exit /b 0
    
    :manual_docker_install
    echo ❌ Automatic Docker installation failed.
    echo Please install Docker Desktop manually from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Install docker-compose if needed
if "%COMPOSE_INSTALLED%"=="false" (
    echo 📥 Installing docker-compose...
    
    REM Try to install docker-compose via pip
    pip install docker-compose
    if errorlevel 1 (
        echo ❌ docker-compose installation failed via pip
        echo Please install Docker Compose manually from: https://github.com/docker/compose/releases
        pause
        exit /b 1
    ) else (
        echo ✅ docker-compose installed successfully via pip
    )
)

REM Test Docker installation
echo 🧪 Testing Docker installation...
docker run --rm hello-world >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Docker installation may need additional configuration
    echo Please ensure Docker Desktop is running
) else (
    echo ✅ Docker is working correctly!
)

echo.
echo 🎉 Docker installation completed successfully!
echo You can now run the DocuSearch startup scripts.

REM Show Docker status
echo.
echo === Docker Status ===
docker --version
docker-compose --version
echo.

pause
