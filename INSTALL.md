# Installation Guide

## System Requirements

### Required Software
1. **Node.js 14+** - For running the WhatsApp bot
2. **Google Chrome** - For Puppeteer/WhatsApp Web automation
3. **WhatsApp** - Mobile app for authentication

### Verify Your System

```bash
# Check Node.js (should be 14.0.0 or higher)
node --version

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

### 3. Run the Bot

```bash
node bot.js
```

### 4. Authenticate with WhatsApp

1. A QR code will appear in your terminal
2. Open WhatsApp on your phone
3. Go to **Settings** → **Linked Devices** → **Link a Device**
4. Scan the QR code
5. Wait for "✅ Ready! Send #help"

### 5. Test It

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

If Chrome is installed elsewhere, edit `bot.js` line 15:

```javascript
executablePath: '/path/to/your/chrome'
```

## Troubleshooting Installation

### "node: command not found"

Install Node.js from https://nodejs.org/

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

## Next Steps

Once installed:
- See [README.md](README.md) for usage instructions
- Try creating your first task with `#task`
- All tasks are saved in `tasks.json`

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
```

Your tasks are in `tasks.json` - back it up if you want to keep them!
