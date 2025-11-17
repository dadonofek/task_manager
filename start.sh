#!/bin/bash
# Start both Flask backend and WhatsApp bot

set -e

echo "=========================================="
echo "Starting WhatsApp Task Manager"
echo "=========================================="
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start Flask backend in background
echo "🚀 Starting Flask backend..."
python3 app.py &
FLASK_PID=$!
echo "✅ Flask backend started (PID: $FLASK_PID)"
echo

# Wait for Flask to start
sleep 3

# Check if we're in automated mode
if [ "$WHATSAPP_MODE" = "automated" ]; then
    echo "🤖 Starting WhatsApp bot..."
    npm start &
    BOT_PID=$!
    echo "✅ WhatsApp bot started (PID: $BOT_PID)"
    echo
    echo "📱 Please scan the QR code with WhatsApp"
    echo
else
    echo "ℹ️  WhatsApp mode is set to 'manual'"
    echo "ℹ️  Bot will not start automatically"
    echo "ℹ️  Change WHATSAPP_MODE to 'automated' in .env to enable bot"
    echo
fi

# Handle Ctrl+C
trap cleanup INT TERM

cleanup() {
    echo
    echo "Shutting down..."
    kill $FLASK_PID 2>/dev/null || true
    [ ! -z "$BOT_PID" ] && kill $BOT_PID 2>/dev/null || true
    echo "✅ Stopped"
    exit 0
}

echo "=========================================="
echo "✅ Task Manager is running!"
echo "=========================================="
echo
echo "Flask backend: http://localhost:5000"
echo
echo "Press Ctrl+C to stop"
echo

# Wait for processes
wait
