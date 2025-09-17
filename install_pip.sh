#!/bin/bash

# DocuSearch - Pip Installation Script
# This script installs pip if it's not already available

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🐍 DocuSearch Pip Installation"
echo "==============================="
echo

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.7 or higher first."
    print_status "Installation instructions:"
    print_status "  - Ubuntu/Debian: sudo apt update && sudo apt install python3"
    print_status "  - CentOS/RHEL: sudo yum install python3"
    print_status "  - macOS: brew install python3"
    print_status "  - Or download from: https://www.python.org/downloads/"
    exit 1
fi

print_success "Python 3 is installed: $(python3 --version)"

# Check if pip is already installed
if command_exists pip3; then
    print_success "pip3 is already installed: $(pip3 --version)"
    print_status "Upgrading pip to latest version..."
    pip3 install --upgrade pip --user
    print_success "pip upgrade completed"
    exit 0
fi

print_warning "pip3 not found. Installing pip..."

# Try different installation methods
install_success=false

# Method 1: Try using ensurepip module
print_status "Trying ensurepip module..."
if python3 -m ensurepip --upgrade --user 2>/dev/null; then
    print_success "pip installed using ensurepip module"
    install_success=true
fi

# Method 2: Try using get-pip.py
if [ "$install_success" = false ]; then
    print_status "Trying get-pip.py method..."
    
    # Check if get-pip.py already exists
    if [ -f "get-pip.py" ]; then
        print_status "Using existing get-pip.py..."
        python3 get-pip.py --user
    else
        print_status "Downloading get-pip.py..."
        if curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py; then
            python3 get-pip.py --user
            rm get-pip.py
        else
            print_error "Failed to download get-pip.py"
        fi
    fi
    
    # Verify installation
    if command_exists pip3; then
        print_success "pip installed using get-pip.py"
        install_success=true
    fi
fi

# Method 3: Try system package manager (if available)
if [ "$install_success" = false ]; then
    print_status "Trying system package manager..."
    
    if command_exists apt-get; then
        print_status "Detected apt package manager. Installing python3-pip..."
        if sudo apt update && sudo apt install -y python3-pip; then
            print_success "pip installed using apt"
            install_success=true
        fi
    elif command_exists yum; then
        print_status "Detected yum package manager. Installing python3-pip..."
        if sudo yum install -y python3-pip; then
            print_success "pip installed using yum"
            install_success=true
        fi
    elif command_exists dnf; then
        print_status "Detected dnf package manager. Installing python3-pip..."
        if sudo dnf install -y python3-pip; then
            print_success "pip installed using dnf"
            install_success=true
        fi
    elif command_exists brew; then
        print_status "Detected Homebrew. Installing python3-pip..."
        if brew install python3; then
            print_success "pip installed using Homebrew"
            install_success=true
        fi
    fi
fi

# Final verification
if [ "$install_success" = true ]; then
    # Add user bin to PATH if pip was installed with --user
    if [ -d "$HOME/.local/bin" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Verify pip installation
    if command_exists pip3; then
        print_success "pip3 installation verified: $(pip3 --version)"
        print_status "Upgrading pip to latest version..."
        pip3 install --upgrade pip --user
        print_success "pip installation and upgrade completed successfully!"
    else
        print_error "pip installation failed verification"
        exit 1
    fi
else
    print_error "All pip installation methods failed"
    print_status "Please install pip manually:"
    print_status "  - Ubuntu/Debian: sudo apt install python3-pip"
    print_status "  - CentOS/RHEL: sudo yum install python3-pip"
    print_status "  - macOS: brew install python3"
    print_status "  - Or visit: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi

echo
print_success "🎉 pip installation completed successfully!"
print_status "You can now run the DocuSearch startup scripts."
