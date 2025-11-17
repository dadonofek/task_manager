#!/bin/bash

# WhatsApp Task Manager - Startup Script
# Runs both Flask backend and WhatsApp bot

echo "🚀 Starting WhatsApp Task Manager..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi

# Use python3 if available, otherwise use python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Node.js dependencies"
        exit 1
    fi
    echo ""
fi

# Check if Python dependencies are installed
echo "🔍 Checking Python dependencies..."
$PYTHON_CMD -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask is not installed. Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Set environment variables
export BASE_URL="${BASE_URL:-http://localhost:5001}"
export WHATSAPP_GROUP_NAME="${WHATSAPP_GROUP_NAME:-Task Manager}"
export WHATSAPP_ENABLED="true"

echo "📋 Configuration:"
echo "   Flask API: http://localhost:5001"
echo "   WhatsApp Group: $WHATSAPP_GROUP_NAME"
echo ""

# Create a trap to kill both processes on exit
trap 'echo ""; echo "🛑 Shutting down..."; kill $(jobs -p) 2>/dev/null; exit' INT TERM

# Start Flask in background
echo "🐍 Starting Flask backend..."
$PYTHON_CMD app.py > flask.log 2>&1 &
FLASK_PID=$!

# Wait a bit for Flask to start
sleep 2

# Check if Flask started successfully
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "❌ Flask failed to start. Check flask.log for details."
    exit 1
fi

echo "✅ Flask backend running (PID: $FLASK_PID)"
echo ""

# Start WhatsApp bot
echo "📱 Starting WhatsApp bot..."
echo "   You'll need to scan a QR code with your phone"
echo ""

node whatsapp_bot.js

# If WhatsApp bot exits, kill Flask too
kill $FLASK_PID 2>/dev/null
