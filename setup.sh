#!/bin/bash
# Setup script for WhatsApp Task Manager

set -e

echo "=========================================="
echo "WhatsApp Task Manager - Setup Script"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18 or higher"
    exit 1
fi

echo "✅ Python and Node.js are installed"
echo

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
echo "✅ Python dependencies installed"
echo

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install
echo "✅ Node.js dependencies installed"
echo

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file to configure your settings"
    echo
else
    echo "ℹ️  .env file already exists, skipping"
    echo
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from database import init_db; init_db()"
echo "✅ Database initialized"
echo

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "1. Edit .env file to configure your WhatsApp integration mode"
echo "2. Start the Flask backend:"
echo "   $ python3 app.py"
echo "3. In a new terminal, start the WhatsApp bot:"
echo "   $ npm start"
echo "4. Scan the QR code with WhatsApp"
echo "5. Create a WhatsApp group called 'My Tasks'"
echo "6. Send a message with #task format to test!"
echo
echo "⚠️  IMPORTANT: Read WHATSAPP_INTEGRATION.md for setup instructions"
echo "⚠️  and risk warnings about WhatsApp automation"
echo
