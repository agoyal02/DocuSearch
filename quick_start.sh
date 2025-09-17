#!/bin/bash

# DocuSearch Quick Start Script
# Simple script to start all services with minimal output

echo "🚀 Starting DocuSearch Services..."

# Create directories if they don't exist
mkdir -p uploads parsed_documents job_results job_metadata schemas

# Check if pip is installed
if ! command -v pip3 >/dev/null 2>&1; then
    echo "⚠️  pip3 not found. Installing pip..."
    if [ -f "get-pip.py" ]; then
        python3 get-pip.py --user
    else
        curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py --user
        rm get-pip.py
    fi
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip in virtual environment
pip install --upgrade pip

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "⚠️  Docker not found. Installing Docker..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo systemctl start docker
            sudo usermod -aG docker $USER
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo systemctl start docker
            sudo usermod -aG docker $USER
        else
            echo "❌ Unsupported Linux distribution. Please install Docker manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install --cask docker
            echo "⚠️  Docker Desktop installed. Please start it manually and run this script again."
            exit 0
        else
            echo "❌ Homebrew not found. Please install Docker Desktop manually."
            exit 1
        fi
    else
        echo "❌ Unsupported OS. Please install Docker manually."
        exit 1
    fi
fi

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "⚠️  docker-compose not found. Installing..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            brew install docker-compose
        else
            echo "❌ Homebrew not found. Please install docker-compose manually."
            exit 1
        fi
    fi
fi

# Start GROBID
echo "🔬 Starting GROBID service..."
docker-compose up -d grobid

# Wait for GROBID
echo "⏳ Waiting for GROBID to be ready..."
sleep 30

# Check GROBID status
if curl -f http://localhost:8070/api/isalive >/dev/null 2>&1; then
    echo "✅ GROBID is ready!"
else
    echo "❌ GROBID failed to start. Check with: docker-compose logs grobid"
    exit 1
fi

# Start the application
echo "🌐 Starting DocuSearch application..."
python3 app.py &
APP_PID=$!

# Wait a moment for the app to start
sleep 5

echo ""
echo "🎉 DocuSearch is now running!"
echo "🌐 Web Interface: http://localhost:5000"
echo "📊 Metrics: http://localhost:5000/metrics"
echo "🛑 To stop: kill $APP_PID && docker-compose down"
echo ""
