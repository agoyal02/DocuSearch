#!/bin/bash

# Start GROBID service using Docker Compose
echo "Starting GROBID service..."
docker-compose up -d grobid

echo "Waiting for GROBID to be ready..."
sleep 30

# Check if GROBID is running
echo "Checking GROBID status..."
curl -f http://localhost:8070/api/isalive

if [ $? -eq 0 ]; then
    echo "✅ GROBID is running and ready!"
    echo "GROBID service is available at: http://localhost:8070"
    echo "You can now start your DocuSearch application with: python app.py"
else
    echo "❌ GROBID failed to start. Check the logs with: docker-compose logs grobid"
fi
