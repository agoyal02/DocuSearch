@echo off
REM DocuSearch - Pip Installation Script for Windows
REM This script installs pip if it's not already available

setlocal enabledelayedexpansion

echo.
echo 🐍 DocuSearch Pip Installation
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version

REM Check if pip is already installed
pip --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ pip is already installed
    pip --version
    echo 📥 Upgrading pip to latest version...
    pip install --upgrade pip --user
    echo ✅ pip upgrade completed
    pause
    exit /b 0
)

echo ⚠️  pip not found. Installing pip...

REM Try to install pip using get-pip.py
if exist "get-pip.py" (
    echo 📥 Using existing get-pip.py...
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
    pip --version
)

echo 📥 Upgrading pip to latest version...
pip install --upgrade pip --user

echo.
echo 🎉 pip installation completed successfully!
echo You can now run the DocuSearch startup scripts.
echo.
pause
