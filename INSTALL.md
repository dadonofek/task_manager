# Installation Guide

## System Requirements

### Required Software
1. **macOS** - For Apple Notes integration (uses JXA)
2. **Node.js 14+** - For running the WhatsApp bot
3. **Python 3.8+** - For Apple Notes integration
4. **Google Chrome** - For Puppeteer/WhatsApp Web
5. **WhatsApp** - Mobile app for authentication

### Verify Your System

```bash
# Check macOS version
sw_vers

# Check Node.js (should be 14.0.0 or higher)
node --version

# Check Python (should be 3.8 or higher)
python3 --version

# Check Chrome is installed
ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

## Installation Steps

### 1. Clone or Download the Repository

```bash
git clone <your-repo-url>
cd task_manager
```

### 2. Install Dependencies

```bash
# Navigate to the WhatsApp bot package
cd simple-whatsapp-bot

# Install Node.js dependencies
npm install

# Go back to project root
cd ..
```

### 3. Set Permissions (macOS Security)

The bot needs permission to:
- Control Apple Notes
- Run scripts

When you first run the bot, macOS may ask for permissions:

1. **System Settings** → **Privacy & Security** → **Automation**
2. Find your terminal app (Terminal, iTerm2, etc.)
3. Enable access to **Notes**

### 4. Run the Bot

```bash
node bot.js
```

### 5. Authenticate with WhatsApp

1. A QR code will appear in your terminal
2. Open WhatsApp on your phone
3. Go to **Settings** → **Linked Devices** → **Link a Device**
4. Scan the QR code
5. Wait for "✅ WhatsApp bot is ready!"

### 6. Test It

Send yourself a WhatsApp message:
```
#help
```

You should get a reply with available commands!

## Optional Configuration

### Listen to Specific Group Only

```bash
WHATSAPP_GROUP="Task Manager" node bot.js
```

### Custom Chrome Path

If Chrome is installed elsewhere, edit `bot.js` line 16:

```javascript
executablePath: '/path/to/your/chrome'
```

## Troubleshooting Installation

### "node: command not found"

Install Node.js from https://nodejs.org/

### "python3: command not found"

Python 3 should be pre-installed on macOS. If not:
```bash
brew install python3
```

### "Chrome not found"

Download and install from https://www.google.com/chrome/

### npm install fails

Make sure you're in the `simple-whatsapp-bot` directory:
```bash
cd simple-whatsapp-bot
npm install
```

### Error -86 (Apple Silicon)

This error occurs when Puppeteer's Chromium is x86_64 on Apple Silicon Macs. The bot is already configured to use your system Chrome instead. Just make sure Chrome is installed.

### Permission Denied for Notes

1. **System Settings** → **Privacy & Security** → **Automation**
2. Find Terminal (or your terminal app)
3. Enable access to Notes
4. Restart the bot

## Next Steps

Once installed:
- See [README.md](README.md) for usage instructions
- See [TODO.md](TODO.md) for planned features
- Try creating your first task!

## Upgrading

To update dependencies:

```bash
cd simple-whatsapp-bot
npm update
cd ..
```

## Uninstalling

To remove:
```bash
# Remove project
rm -rf task_manager/

# WhatsApp auth data is stored in .wwebjs_auth
# This is already in project folder, so deleted above
```

Your Apple Notes remain untouched in the Notes app.
