# WhatsApp Integration Guide

## 🎯 Overview

This task manager now supports **two modes** of WhatsApp integration:

1. **Automated Mode** (NEW!) - Automatically reads messages from a dedicated WhatsApp group
2. **Manual Mode** - Original URL-based approach (safest, zero ban risk)

## ⚠️ CRITICAL WARNING

**Using automated WhatsApp integration (whatsapp-web.js) violates WhatsApp's Terms of Service and may result in your account being permanently banned.**

### Risk Assessment

| Mode | Ban Risk | Setup Complexity | User Experience |
|------|----------|------------------|-----------------|
| **Automated** | ⚠️ **HIGH** | Medium | Excellent |
| **Manual** | ✅ None | Low | Good |

### Recommendations

- ✅ **Use a secondary phone number** for automated mode
- ✅ **Start with manual mode** to test the system
- ✅ **Monitor only ONE dedicated group** to reduce detection risk
- ✅ **Enable rate limiting** and quiet hours
- ✅ **Have a backup plan** if your account gets banned

## 📱 Automated Mode - How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│  WhatsApp Group: "My Tasks"            │
│  (You + Your Family)                   │
└────────────────┬────────────────────────┘
                 │
                 │ Message with #task format
                 ↓
┌─────────────────────────────────────────┐
│  WhatsApp Bot (whatsapp-web.js)        │
│  • Monitors group messages              │
│  • Detects #task format                 │
│  • Parses task details                  │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP POST /api/newTask
                 ↓
┌─────────────────────────────────────────┐
│  Flask Backend                          │
│  • Creates task in database             │
│  • Generates quick action URLs          │
│  • Returns task details                 │
└────────────────┬────────────────────────┘
                 │
                 │ Auto-reply with links
                 ↓
┌─────────────────────────────────────────┐
│  WhatsApp Group                         │
│  ✅ Task #15 Created!                   │
│  📋 Buy groceries                       │
│  🔗 Quick Actions: [links]              │
└─────────────────────────────────────────┘
```

### Setup Instructions

#### 1. Install Dependencies

```bash
# Run the setup script
./setup.sh
```

Or manually:

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

#### 2. Configure Environment

Edit `.env` file:

```bash
# Set to automated mode
WHATSAPP_MODE=automated

# Configure your backend URL
BACKEND_URL=http://localhost:5000

# Name of the WhatsApp group to monitor
WHATSAPP_GROUP_NAME=My Tasks

# Enable auto-replies
AUTO_REPLY_ENABLED=true

# Rate limiting (tasks per hour)
MAX_TASKS_PER_HOUR=20

# Quiet hours (24-hour format)
QUIET_HOURS=23-07
```

#### 3. Create WhatsApp Group

1. Open WhatsApp on your phone
2. Create a new group: **"My Tasks"** (must match `WHATSAPP_GROUP_NAME`)
3. Add family members or keep it solo
4. This group will be used exclusively for task management

#### 4. Start the Services

**Option A: Start everything together**
```bash
./start.sh
```

**Option B: Start services separately**
```bash
# Terminal 1 - Flask backend
python3 app.py

# Terminal 2 - WhatsApp bot
npm start
```

#### 5. Authenticate WhatsApp

1. When you start the bot, a QR code will appear in the terminal
2. Open WhatsApp on your phone
3. Go to: **Settings → Linked Devices → Link a Device**
4. Scan the QR code
5. Wait for "✅ WhatsApp client is ready!" message

#### 6. Test It!

Send a message to your "My Tasks" group:

```
#task
Title: Test the bot
Owner: Ofek
Due: Today 6pm
Next: Verify it works
```

You should receive an auto-reply with task confirmation and quick action links!

### Features

✅ **Automatic Task Creation** - Just send #task messages to the group
✅ **Instant Confirmation** - Bot replies with task details and links
✅ **Quick Action Links** - Mark done, reassign, view task
✅ **Rate Limiting** - Prevents spam detection (20 tasks/hour by default)
✅ **Quiet Hours** - Bot sleeps during configured hours (11 PM - 7 AM by default)
✅ **Session Persistence** - QR code only needed once
✅ **Group-Only Monitoring** - Only watches your dedicated task group

### Task Message Format

The bot recognizes messages starting with `#task` followed by key-value pairs:

```
#task
Title: [Required] Task description
Owner: [Required] Person responsible
Due: [Optional] When it's due (flexible format)
Next: [Optional] Next step
Notes: [Optional] Additional info
```

**Examples:**

```
#task
Title: Buy groceries
Owner: Wife
Due: Today 6pm
Next: Ofek picks up
```

```
#task
Title: Call dentist
Owner: Ofek
Due: Tomorrow 2pm
```

```
#task
Title: Pay electricity bill
Owner: Wife
Next: Check email for amount
Notes: Due by end of month
```

### Troubleshooting

**QR Code not appearing?**
- Make sure Node.js 18+ is installed: `node --version`
- Delete `.wwebjs_auth` folder and try again
- Check that port 5000 is not blocked

**Bot not responding to messages?**
- Verify the group name matches exactly: `WHATSAPP_GROUP_NAME=My Tasks`
- Check Flask backend is running: `curl http://localhost:5000/health`
- Look for errors in bot terminal output
- Verify message starts with `#task`

**"Rate limit reached" error?**
- You've hit the hourly limit (default: 20 tasks/hour)
- Wait for the counter to reset
- Increase `MAX_TASKS_PER_HOUR` in .env

**Session expired / QR code again?**
- Session files may be corrupted
- Delete `.wwebjs_auth` folder
- Restart bot and scan QR again
- Enable `SAVE_SESSION=true` in .env

**Account banned?**
- ⚠️ This is the risk of using automated mode
- Switch to manual mode immediately
- Use a different number if possible
- WhatsApp bans are usually permanent

### Risk Mitigation Strategies

1. **Use a Secondary Number**
   - Get a secondary SIM card or virtual number
   - Use that for the bot
   - Keep your main number safe

2. **Minimize Activity**
   - Enable rate limiting (default: 20/hour)
   - Enable quiet hours (default: 11 PM - 7 AM)
   - Don't process every single message

3. **Monitor Only One Group**
   - Create a dedicated "My Tasks" group
   - Don't monitor all chats
   - Keep group small (family only)

4. **Be Human-Like**
   - Don't reply instantly (add small delays if needed)
   - Don't run 24/7 (use quiet hours)
   - Don't process too many messages

5. **Have a Fallback**
   - Be ready to switch to manual mode
   - Export your tasks regularly
   - Keep task data in SQLite database

## 🔗 Manual Mode - Original Approach

If automated mode is too risky, use the manual URL-based approach:

### How It Works

1. **Compose task in WhatsApp** using #task format
2. **Copy the message text**
3. **Open URL** (via keyboard shortcut or bookmark):
   ```
   https://your-app.com/newTask?text=<paste-task-here>
   ```
4. **Backend creates task** and shows quick action links
5. **Save links** in WhatsApp or as shortcuts

### Setup

1. Set `WHATSAPP_MODE=manual` in .env
2. Deploy Flask backend to a server (Railway, Fly.io, etc.)
3. Create iPhone keyboard shortcuts (see QUICKSTART.md)
4. Use starred messages in WhatsApp for quick access

### Advantages

✅ **Zero ban risk** - No automation involved
✅ **Simple setup** - Just Flask backend
✅ **Works anywhere** - Any phone, any platform
✅ **Free hosting** - Railway/Fly.io free tiers

### Disadvantages

❌ Manual copy/paste required
❌ Extra step to create tasks
❌ Need to save quick action links

## 🔄 Switching Between Modes

You can easily switch between automated and manual modes:

1. **To switch to manual:**
   ```bash
   # Edit .env
   WHATSAPP_MODE=manual

   # Restart (only Flask needed)
   python3 app.py
   ```

2. **To switch to automated:**
   ```bash
   # Edit .env
   WHATSAPP_MODE=automated

   # Restart both services
   ./start.sh
   ```

Your tasks are stored in the SQLite database and persist across mode switches.

## 📊 Comparison Table

| Feature | Automated Mode | Manual Mode |
|---------|---------------|-------------|
| **Auto-read messages** | ✅ Yes | ❌ No |
| **Auto-reply** | ✅ Yes | ❌ No |
| **Ban risk** | ⚠️ High | ✅ None |
| **Setup complexity** | Medium | Low |
| **Server requirements** | Flask + Node.js | Flask only |
| **User steps** | 1 (send message) | 3 (copy → open URL → save) |
| **Cost** | Free | Free |
| **Recommended for** | Tech-savvy, secondary number | Everyone |

## 🎓 Best Practices

### For Automated Mode

1. **Start Slow**
   - Test with manual mode first
   - Switch to automated after you're comfortable
   - Use a secondary number if possible

2. **Configure Carefully**
   - Set reasonable rate limits
   - Enable quiet hours
   - Monitor only one group

3. **Monitor Health**
   - Check logs regularly
   - Watch for WhatsApp warnings
   - Have manual mode ready as backup

4. **Be Prepared**
   - Export tasks regularly
   - Have backup contact methods
   - Accept the ban risk

### For Manual Mode

1. **Setup Shortcuts**
   - Create iPhone keyboard shortcuts
   - Save quick action links as contacts
   - Use WhatsApp starred messages

2. **Optimize Workflow**
   - Keep task format template handy
   - Use copy/paste efficiently
   - Bookmark common URLs

3. **Stay Organized**
   - Check /open regularly
   - Use /today for daily planning
   - Review /mine for personal tasks

## 🚀 Next Steps

1. **Choose your mode** (start with manual if unsure)
2. **Run setup script**: `./setup.sh`
3. **Configure .env** file
4. **Start services**: `./start.sh` or separately
5. **Create WhatsApp group** (automated mode only)
6. **Test with sample task**
7. **Enjoy seamless task management!**

## 📞 Support

- Issues? Check logs in terminal output
- Questions? Open GitHub issue
- Need help? Read QUICKSTART.md and EXAMPLES.md

---

**Remember: Use automated mode at your own risk. WhatsApp does not officially support bots!**
