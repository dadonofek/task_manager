# WhatsApp Integration Setup Guide

This guide will help you set up the WhatsApp bot integration for your Task Manager.

## Prerequisites

1. **Node.js** (v14 or higher)
   - Check: `node --version`
   - Download: https://nodejs.org/

2. **Python** (3.7 or higher) - Already installed
   - Check: `python3 --version`

3. **WhatsApp Account**
   - You'll use your personal WhatsApp account
   - A smartphone with WhatsApp installed

4. **WhatsApp Group**
   - Create a WhatsApp group for task management
   - Name it exactly "Task Manager" (or configure a custom name)

## Installation

### 1. Install Node.js Dependencies

```bash
npm install
```

This installs:
- `whatsapp-web.js` - WhatsApp Web API client
- `qrcode-terminal` - QR code display in terminal
- `axios` - HTTP client for API calls

### 2. Configure Your WhatsApp Group

Edit your WhatsApp group name or set environment variable:

**Option A: Rename your WhatsApp group**
- Open WhatsApp
- Go to your task management group
- Rename it to: `Task Manager`

**Option B: Configure custom group name**
```bash
export WHATSAPP_GROUP_NAME="Your Custom Group Name"
```

Or create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env`:
```
WHATSAPP_GROUP_NAME=Family Tasks
```

## Running the Bot

### Quick Start (Recommended)

Use the provided startup script:

```bash
./start.sh
```

This will:
1. Check dependencies
2. Start Flask backend (port 5001)
3. Start WhatsApp bot
4. Display QR code for authentication

### Manual Start

If you prefer to run services separately:

**Terminal 1 - Flask Backend:**
```bash
python app.py
```

**Terminal 2 - WhatsApp Bot:**
```bash
node whatsapp_bot.js
```

## First Time Setup

### Authenticate with WhatsApp

1. Run the bot: `./start.sh`
2. A QR code will appear in your terminal
3. Open WhatsApp on your phone
4. Go to: **Settings** → **Linked Devices** → **Link a Device**
5. Scan the QR code from your terminal
6. Wait for "✅ WhatsApp bot is ready!" message

**Authentication is saved locally**, so you only need to scan once. The session persists in `.wwebjs_auth/` directory.

### Test the Bot

Send a message in your WhatsApp group:

```
#help
```

You should receive a help message with all available commands!

## Using the Bot

### Create a Task

In your WhatsApp group, send:

```
#task
Title: Buy groceries
Owner: Ofek
Due: Tomorrow 6pm
Next: Make shopping list
```

The bot will reply with:
- ✅ Confirmation
- Task details
- Quick action links (mark done, reassign, view)

### List All Tasks

```
#tasks
```
or
```
#list
```

### List Your Tasks

```
#my
```

To see someone else's tasks:
```
#my Shachar
```

### Get Help

```
#help
```
or
```
#?
```

## Quick Actions

When a task is created, the bot sends quick action links:

- **Mark Done:** Tap to complete the task
- **Reassign:** Tap to reassign to Ofek or Shachar
- **View:** Open task details in browser

These links work on **any device** - just tap them in WhatsApp!

## Configuration

### Environment Variables

Create a `.env` file or export these variables:

```bash
# Required
WHATSAPP_GROUP_NAME=Task Manager

# Optional
BASE_URL=http://localhost:5001
FLASK_API_URL=http://localhost:5001
DEBUG=false
```

### Changing User Names

Edit `config.py`:

```python
USERS = ['Ofek', 'Shachar', 'Mom']  # Add more users
```

The bot will automatically use these names for reassignment options.

## Troubleshooting

### QR Code Won't Scan

- Make sure you're using WhatsApp on your phone (not WhatsApp Web)
- Try resizing your terminal window
- Check that QR code is fully visible
- Restart the bot: `Ctrl+C` then `./start.sh`

### "Authentication failed"

- Delete authentication data: `rm -rf .wwebjs_auth`
- Restart and scan QR code again

### Bot Doesn't Respond

1. Check Flask is running: `curl http://localhost:5001/health`
2. Verify group name matches exactly: Check `WHATSAPP_GROUP_NAME`
3. Check bot logs for errors
4. Test in the correct WhatsApp group

### "Could not parse task"

Make sure your message format is exact:
```
#task
Title: Your title here
Owner: Ofek
Due: Tomorrow 5pm
```

- Each field on its own line
- Colon (`:`) after field name
- Correct spelling of fields

### Port 5000/5001 Already in Use

```bash
# Find process using port
lsof -i :5001

# Kill process (replace PID)
kill -9 <PID>

# Or use different port
export BASE_URL=http://localhost:5002
python app.py
```

On macOS, disable AirPlay Receiver:
**System Settings** → **General** → **AirDrop & Handoff** → Turn off **AirPlay Receiver**

## Architecture

```
┌─────────────────────┐
│  WhatsApp Group     │
│  (Users send        │
│   commands)         │
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  whatsapp_bot.js    │
│  (Node.js)          │
│  - Listens to msgs  │
│  - Parses commands  │
│  - Sends replies    │
└─────────┬───────────┘
          │
          │ HTTP API
          ↓
┌─────────────────────┐
│  Flask Backend      │
│  (Python)           │
│  - Task CRUD        │
│  - Database         │
│  - Web UI           │
└─────────────────────┘
```

## Production Deployment

### Security Notes

⚠️ **This is designed for personal/family use**

Before deploying publicly:
1. Add authentication to Flask API
2. Use HTTPS for all URLs
3. Validate all inputs
4. Rate limit API endpoints
5. Monitor for abuse

### Deploying to Server

1. Deploy Flask on a server (Railway, Render, DigitalOcean, etc.)
2. Update `BASE_URL` to your public URL
3. Run WhatsApp bot on a machine that's always on (home server, VPS, etc.)
4. Keep bot running with PM2:

```bash
npm install -g pm2
pm2 start whatsapp_bot.js --name whatsapp-tasks
pm2 save
pm2 startup
```

### Using ngrok for Testing

To test with public URLs without deploying:

```bash
# Terminal 1 - Start services
./start.sh

# Terminal 2 - Expose with ngrok
ngrok http 5001
```

Update your `.env` with the ngrok URL:
```
BASE_URL=https://your-ngrok-url.ngrok.io
```

## Advanced Usage

### Multiple Groups

To monitor multiple groups, modify `whatsapp_bot.js`:

```javascript
const ALLOWED_GROUPS = ['Task Manager', 'Family Tasks', 'Work Tasks'];

if (!ALLOWED_GROUPS.includes(chat.name)) {
    return;
}
```

### Custom Commands

Add your own commands in `whatsapp_bot.js`:

```javascript
else if (messageBody.toLowerCase() === '#urgent') {
    // Your custom command logic
    const urgentTasks = await getUrgentTasks();
    await message.reply(`🚨 Urgent tasks: ${urgentTasks.length}`);
}
```

### Scheduled Reminders

Use cron or node-schedule to send automatic reminders:

```javascript
const schedule = require('node-schedule');

schedule.scheduleJob('0 9 * * *', async () => {
    // Send daily reminder at 9 AM
    const chat = await client.getChatByName('Task Manager');
    await chat.sendMessage('🌅 Good morning! You have X tasks due today.');
});
```

## FAQ

**Q: Can I use this with WhatsApp Business?**
A: Yes! Works with both regular WhatsApp and WhatsApp Business accounts.

**Q: Will this work on multiple devices?**
A: Yes! Once authenticated, the bot runs independently. You can still use WhatsApp on your phone normally.

**Q: Can multiple people use the bot?**
A: Yes! Anyone in the group can send commands and create tasks.

**Q: Is my data secure?**
A: The bot runs locally on your machine. Messages are processed locally and sent to your Flask API. Nothing is stored by WhatsApp Web API.

**Q: Can I use this with multiple WhatsApp accounts?**
A: Each bot instance can only connect to one WhatsApp account. To use multiple accounts, run multiple bot instances in different directories.

## Support

If you encounter issues:

1. Check the logs: `cat flask.log`
2. Enable debug mode: Set `DEBUG=true` in `.env`
3. Check WhatsApp Web status: https://web.whatsapp.com/
4. Verify Node.js and Python versions

## Next Steps

1. ✅ Set up your WhatsApp group
2. ✅ Run `./start.sh` and scan QR code
3. ✅ Send `#help` to test
4. ✅ Create your first task with `#task`
5. 🎉 Enjoy seamless task management!

---

**Made with ❤️ for family task management**
