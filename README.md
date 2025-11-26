# WhatsApp Task Manager - Compact Edition

**Ultra-simple task management using WhatsApp + JSON. No database, no web UI, just clean and simple code.**

Perfect for personal use or small families.

## ✨ What Makes This Special

- 🎯 **Ultra Compact** - Just 1 JavaScript file (124 lines)
- 📱 **WhatsApp Interface** - Create and manage tasks via WhatsApp messages
- 💾 **JSON Storage** - Tasks stored in a clean, readable JSON file
- 📖 **Easy to Read** - Open tasks.json in any text editor to see all tasks
- 🚫 **No Database** - No SQLite, no SQL, no migrations
- 🚫 **No Web Server** - No Flask, no HTML, no port conflicts
- 🚫 **No Python** - Pure JavaScript, runs on Node.js
- 🖥️ **Cross-Platform** - Works on macOS, Linux, Windows

## 🚀 Quick Start

### Prerequisites
- **Node.js 14+** (for WhatsApp bot)
- **Google Chrome** (for WhatsApp Web automation)
- **WhatsApp** on your phone

### 1. Install

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

**Quick install:**
```bash
git clone <your-repo>
cd task_manager

# Install Node dependencies for WhatsApp bot
cd simple-whatsapp-bot
npm install
cd ..
```

### 2. Run

```bash
node bot.js
```

Or listen to specific WhatsApp group:
```bash
WHATSAPP_GROUP="Task Manager" node bot.js
```

### 3. Authenticate

1. QR code appears in terminal
2. Open WhatsApp → Settings → Linked Devices → Link a Device
3. Scan the QR code
4. Done! Bot is ready

### 4. Test

Send this to yourself or your group in WhatsApp:
```
#help
```

Bot should reply with available commands! 🎉

## 📱 How to Use

### Create a Task

Send this in WhatsApp:
```
#task
Title: Buy groceries
Owner: Ofek
Due: Tomorrow 6pm
Next: Make shopping list
Priority: high
```

Bot replies:
```
✅ Task created!

📝 Buy groceries
👤 Owner: Ofek
📅 Due: Tomorrow 6pm

🆔 ID: task_20251126_143052

Use '#done task_20251126_143052' to mark complete
```

**The task is now saved in tasks.json - open it anytime to see all your tasks!**

### List All Tasks

```
#tasks
```

or

```
#list
```

Bot replies with all open tasks, sorted by priority (high → medium → low).

### List Your Tasks

```
#mine Ofek
```

Shows only tasks assigned to Ofek.

### Mark Task Done

```
#done task_20251126_143052
```

Updates the task status in tasks.json.

### Get Help

```
#help
```

Shows all available commands.

## 📝 What Happens Behind the Scenes

1. **You send #task message** → Bot parses it
2. **Bot saves to JSON** → Writes to tasks.json
3. **Bot replies** → Confirmation with task ID

**That's it!** No syncing, no background processes, just instant reads and writes to a clean JSON file.

## 📄 How Tasks Look in JSON

Open `tasks.json` to see:

```json
[
  {
    "id": "task_20251126_143052",
    "title": "Buy groceries",
    "owner": "Ofek",
    "due": "Tomorrow 6pm",
    "next": "Make shopping list",
    "priority": "high",
    "status": "open",
    "created_at": "2025-11-26T14:30:52.123Z",
    "completed_at": null
  }
]
```

Clean, readable, easy to edit!

## 📋 Task Format

### Required Fields
- `Title:` - What needs to be done
- `Owner:` - Who is responsible

### Optional Fields
- `Due:` - When it's due (natural language OK: "tomorrow", "next Friday 5pm")
- `Next:` - Next action step
- `Priority:` - high, medium, or low (default: medium)
- `Notes:` - Additional details

### Example
```
#task
Title: Upload medical documents
Owner: Wife
Due: Thu 20:00
Next: Scan passport and ID
Priority: high
Notes: Remember both pages of ID
```

## 🗂️ File Structure

```
task_manager/
├── bot.js                   # Main bot (124 lines) - Everything!
├── tasks.json               # Your tasks database (auto-created)
├── simple-whatsapp-bot/     # WhatsApp integration (reusable package)
└── README.md                # This file
```

**Total implementation: 1 JavaScript file, 124 lines.**

## 🔧 Architecture

```
WhatsApp Messages
       ↓
   bot.js (Node.js)
       ↓
   tasks.json (read/write)
```

**That's it! Super simple.**

**Key Design Decisions:**
- **Pure JavaScript** - No mixing languages, no subprocesses
- **JSON = Storage** - Simple, readable, easy to version control
- **No Database** - fs.readFileSync and fs.writeFileSync are enough
- **No Web UI** - Just open tasks.json in any text editor

## 🎯 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `#task` | Create new task | See format above |
| `#tasks` or `#list` | Show all open tasks | `#tasks` |
| `#mine <name>` | Show tasks for owner | `#mine Ofek` |
| `#done <id>` | Mark task complete | `#done task_20251126_143052` |
| `#help` | Show help message | `#help` |

## 💡 Pro Tips

### 1. Edit tasks.json Directly
You can edit tasks.json in any text editor! Just reload the bot or send a message to refresh.

### 2. Version Control
Add tasks.json to git (or exclude it) - your choice! Easy to backup and track changes.

### 3. View Anytime
Open tasks.json to see all tasks instantly - no need to message the bot.

### 4. Natural Language Dates
These all work:
- "Tomorrow 6pm"
- "Next Friday at 3"
- "Thu 20:00"
- "Dec 25"

### 5. Group vs. Personal
- Use `WHATSAPP_GROUP="Task Manager" node bot.js` to listen only to specific group
- Omit to listen to all WhatsApp messages

## 🧪 Testing

### Test Task Creation
```
#task
Title: Test task
Owner: Me
Priority: high
```

Check:
1. Bot replies with confirmation
2. tasks.json file is created/updated
3. Open tasks.json to verify the task is there

### Test Listing
```
#tasks
```

Should show the task you just created.

### Test Completion
```
#done task_xxxxx
```

(Use the actual task ID from creation)

Check:
1. Bot confirms completion
2. tasks.json updated with status: "done" and completed_at timestamp

## 🔧 Troubleshooting

### Bot Not Responding

**Check bot is running:**
```bash
# Should show node bot.js process
ps aux | grep "node bot"
```

**Check for errors:**
- Look at terminal output
- Errors will be printed to console

**Restart:**
```bash
# Kill bot
Ctrl+C

# Restart
node bot.js
```

### Tasks Not Saving

**Check file permissions:**
```bash
# Make sure you can write to the directory
touch tasks.json
ls -la tasks.json
```

**Check tasks.json format:**
- Must be valid JSON
- If corrupted, delete and restart bot

### WhatsApp Authentication Lost

If bot stops receiving messages:

```bash
# Remove auth cache
rm -rf .wwebjs_auth .wwebjs_cache

# Restart bot
node bot.js

# Scan QR code again
```

### Chrome/Puppeteer Errors

**Error: "spawn Unknown system error -86"**

This happens on Apple Silicon Macs when Chromium binary is x86_64. The bot is configured to use your system Chrome instead.

**Make sure Chrome is installed:**
```bash
ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
```

**If Chrome is not found**, install it from https://www.google.com/chrome/

**If Chrome is in a different location**, edit bot.js:15-17 to point to your Chrome path.

### QR Code Won't Scan

- **Terminal too small?** Make it bigger
- **QR code cut off?** Scroll up
- **Still doesn't work?** Try different terminal (Terminal.app, iTerm2)

### Tasks.json Corrupted

```bash
# Backup old file
mv tasks.json tasks.json.backup

# Bot will create fresh empty file
node bot.js
```

## 🚀 Advanced Usage

### Run in Background

**Using nohup:**
```bash
nohup node bot.js > bot.log 2>&1 &
```

**Using screen:**
```bash
screen -S taskbot
node bot.js
# Press Ctrl+A, then D to detach
```

**To reconnect:**
```bash
screen -r taskbot
```

### Multiple Groups

Run separate bots for different groups:

```bash
# Terminal 1
WHATSAPP_GROUP="Work Tasks" node bot.js

# Terminal 2
WHATSAPP_GROUP="Family Tasks" node bot.js
```

Each bot maintains its own:
- Apple Notes folder ("Tasks" by default)
- JSON backup (tasks.json)
- WhatsApp session

### Custom JSON File Location

Edit `bot.js`:
```javascript
const TASKS_JSON = 'my_tasks.json';  // Change filename/path
```

## 📊 Data Storage

### JSON File
- **Location**: `tasks.json` in project directory
- **Format**: JSON array of task objects
- **Readable**: Open in any text editor
- **Editable**: Edit directly if needed (bot will pick up changes)
- **Backup**: Easy to backup, version control, or sync

### Example tasks.json
```json
[
  {
    "id": "task_20251126_143052",
    "title": "Buy groceries",
    "owner": "Ofek",
    "due": "Tomorrow 6pm",
    "next": "Make shopping list",
    "priority": "high",
    "status": "open",
    "created_at": "2025-11-26T14:30:52",
    "completed_at": null,
    "note_id": "x-coredata://ABCD-1234"
  }
]
```

## 🎨 Customization

### Add Custom Fields

Edit `bot.js` → `parseTask()` function:

```javascript
const map = {
    title:'title',
    owner:'owner',
    due:'due',
    next:'next',
    priority:'priority',
    location:'location',  // Add this
    cost:'cost'           // Add this
};
```

Then in WhatsApp:
```
#task
Title: Buy coffee
Owner: Me
Location: Trader Joe's
Cost: $15
```

### Change Emoji

Edit `bot.js` → `formatList()` function:

```javascript
const e = {
    high:'🔥',     // Change from 🔴
    medium:'⭐',   // Change from 🟡
    low:'💤'       // Change from 🟢
}[t.priority] || '🟡';
```

### Custom Reply Messages

Edit `bot.js` → around line 124:

```javascript
msg.reply(`🎉 Boom! Task created!\n📝 ${t.title}\n...`);  // Customize this
```

## 🔒 Security Notes

### This is for Personal/Family Use

⚠️ **Not designed for:**
- Public deployment
- Untrusted users
- Production systems
- Large teams

⚠️ **No built-in:**
- Authentication
- Authorization
- Rate limiting
- Input sanitization (basic only)
- Encryption

### Protect Your Data

1. **Don't commit sensitive data:**
   ```bash
   # Already in .gitignore:
   tasks.json
   .wwebjs_auth/
   .wwebjs_cache/
   ```

2. **Backup regularly:**
   - tasks.json
   - Apple Notes (via iCloud/Time Machine)

3. **Keep bot private:**
   - Don't share WhatsApp session
   - Don't expose to internet
   - Run on trusted machine only

## 📈 Limitations

### Current Constraints

- **Single user per bot** - One WhatsApp connection per bot instance
- **JSON storage** - Not optimized for huge datasets (but fine for 1000s of tasks)
- **Text only** - No image/file attachments (yet)
- **Simple search** - No full-text search (just list/filter)
- **No concurrent writes** - One bot instance per JSON file

### When to Upgrade

Consider more robust solution if you need:
- **>10,000 tasks** - SQLite would be faster
- **Multiple users** - Need proper database with permissions
- **Complex queries** - Need SQL for joins/aggregations
- **Web UI** - Need Flask/React
- **Concurrent access** - Need database with locking

See [TODO.md](TODO.md) for planned features and workarounds.

## 🛠️ Development

### Project Structure

```
bot.js                  # Main task manager bot (124 lines!)
├── loadTasks()         # Read from JSON
├── saveTasks()         # Write to JSON
├── parseTask()         # Parse WhatsApp messages
└── formatList()        # Format task lists

simple-whatsapp-bot/    # Reusable WhatsApp bot package
├── src/
│   └── WhatsAppBot.js  # Main bot class
├── examples/           # Usage examples
└── package.json
```

### Key Technologies

- **Node.js** - Main runtime
- **whatsapp-web.js** - WhatsApp Web protocol (via Puppeteer)
- **Puppeteer** - Headless Chrome automation
- **fs** - File system for JSON storage
- **JSON** - Data storage format

### Code Style

- **Simple > Clever** - Readable code over optimizations
- **Pure functions** - loadTasks(), saveTasks() do one thing
- **Log everything** - Print status to terminal
- **No magic** - Explicit is better than implicit

## 🤝 Contributing

Want to improve this? Here's how:

1. **Fork** the repo
2. **Create branch**: `git checkout -b feature/my-feature`
3. **Make changes** - Keep it simple!
4. **Test thoroughly** - Create, list, complete tasks
5. **Submit PR** - Explain what and why

### Ideas Welcome

See [TODO.md](TODO.md) for planned features. Have other ideas? Open an issue!

## 📄 License

MIT License - Use freely, modify as needed, no attribution required.

## 💡 Why This Design?

### The Problem

Most task managers are either:
1. **Too complex** - Need server, database, authentication, deployment
2. **Too limited** - Just a todo list, no collaboration
3. **Platform-locked** - iOS only, Android only, web only

### The Solution

This bot is intentionally **ultra-simple**:
- ✅ No database setup - Just a JSON file
- ✅ No web server - Just Node.js script
- ✅ No deployment - Runs locally
- ✅ No app install - Uses WhatsApp you already have
- ✅ No cloud costs - Everything local
- ✅ No learning curve - Natural conversation
- ✅ Cross-platform - Works on any OS with Node.js

### Perfect For

- Small families coordinating tasks
- Personal task tracking
- Quick task capture from WhatsApp
- People who like JSON and text files
- Developers who want simple, hackable code
- Anyone who values simplicity

### Not For

- Large teams (no permissions/roles)
- Public/commercial use (no auth)
- Mission-critical systems (no HA/redundancy)
- Very large datasets (>10,000 tasks)

## 🎉 Success Stories

Using this bot? Share your experience! Open an issue with tag `showcase`.

---

**Built with ❤️ for people who value simplicity over features**

*Questions? Check [TODO.md](TODO.md) for roadmap or open an issue!*
