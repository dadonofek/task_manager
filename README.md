# WhatsApp Task Manager - Compact Edition

**Ultra-simple task management using WhatsApp + Apple Notes. No database, no web UI, just clean and simple code.**

Perfect for personal use or small families on macOS.

## ✨ What Makes This Special

- 🎯 **Ultra Compact** - Just 1 JavaScript bot + 1 Python helper (~600 lines total)
- 📱 **WhatsApp Interface** - Create and manage tasks via WhatsApp messages
- 📝 **Apple Notes Storage** - Tasks stored as notes (visible across all your Apple devices)
- 💾 **JSON Backup** - Automatic backup to tasks.json
- 🔄 **Auto-Sync** - Bidirectional sync between Notes and WhatsApp every 5 minutes
- 🚫 **No Database** - No SQLite, no SQL, no migrations
- 🚫 **No Web Server** - No Flask, no HTML, no port conflicts
- 🎨 **Beautiful Notes** - Tasks formatted with emoji and structure

## 🚀 Quick Start

### Prerequisites
- **macOS** (required for Apple Notes)
- **Python 3.8+** (for Apple Notes integration)
- **Node.js 14+** (for WhatsApp bot)
- **Google Chrome** (installed at `/Applications/Google Chrome.app`)
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

**The task now appears in your Apple Notes app in the "Tasks" folder!**

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

Updates the task in both Apple Notes and the backup file.

### Get Help

```
#help
```

Shows all available commands.

## 📝 What Happens Behind the Scenes

1. **You send #task message** → Bot parses it
2. **Bot creates Apple Note** → Formatted with emoji and structure
3. **Bot saves to JSON** → Backup in tasks.json
4. **Bot replies** → Confirmation with task ID

**Every 5 minutes:**
- Bot syncs from Apple Notes (source of truth)
- Updates JSON backup
- You can edit tasks directly in Apple Notes app!

## 🎨 How Tasks Look in Apple Notes

```
🔴 [HIGH] Buy groceries

👤 Owner: Ofek
📅 Due: Tomorrow 6pm
➡️ Next: Make shopping list

Status: ⚪ Open
Created: 2025-11-26 14:30
ID: task_20251126_143052
```

- 🔴 Red for high priority
- 🟡 Yellow for medium priority
- 🟢 Green for low priority
- ⚪ Open status / ✅ Done status

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
├── bot.js                   # Main bot (160 lines) - WhatsApp + orchestration
├── apple_notes.py           # Apple Notes client (300 lines) - JXA wrapper
├── tasks.json               # Auto-generated backup
├── simple-whatsapp-bot/     # WhatsApp integration (reusable package)
└── README.md                # This file
```

**Total implementation: 1 JavaScript file + 1 Python helper, ~460 lines total.**

## 🔧 Architecture

```
WhatsApp Messages
       ↓
   bot.js (Node.js - parses messages)
       ↓
   spawns Python subprocess
       ↓
   apple_notes.py (JXA wrapper)
       ↓
   osascript -l JavaScript
       ↓
   Apple Notes App (macOS)
       ↓
   tasks.json (backup)
```

**Key Design Decisions:**
- **JavaScript for WhatsApp** - Uses whatsapp-web.js (best maintained library)
- **Python for Apple Notes** - Uses JXA via osascript (macOS native)
- **Bridge via subprocess** - Clean separation, each language does what it's best at
- **Apple Notes = Primary Storage** - Source of truth, syncs across devices
- **JSON = Backup** - Fast reads, offline access
- **No Database** - Simpler, fewer dependencies
- **No Web UI** - Apple Notes app is the UI

## 🎯 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `#task` | Create new task | See format above |
| `#tasks` or `#list` | Show all open tasks | `#tasks` |
| `#mine <name>` | Show tasks for owner | `#mine Ofek` |
| `#done <id>` | Mark task complete | `#done task_20251126_143052` |
| `#help` | Show help message | `#help` |

## 💡 Pro Tips

### 1. Edit in Apple Notes
You can edit tasks directly in the Apple Notes app! Changes sync back to WhatsApp every 5 minutes.

### 2. Use Siri
"Hey Siri, show me my Tasks notes" → Opens your task list

### 3. iPhone Widgets
Add Apple Notes widget to your home screen → Always see your tasks

### 4. Natural Language Dates
These all work:
- "Tomorrow 6pm"
- "Next Friday at 3"
- "Thu 20:00"
- "Dec 25"

### 5. Group vs. Personal
- Use `--group "Task Manager"` to listen only to specific group
- Omit `--group` to listen to all WhatsApp messages

## 🔄 Auto-Sync

The bot automatically syncs every 5 minutes:

1. Reads all notes from Apple Notes "Tasks" folder
2. Parses them back to task dictionaries
3. Compares with local cache
4. Updates JSON backup
5. Detects if you edited notes directly

**This means you can:**
- Edit tasks in Apple Notes app
- Changes reflect in WhatsApp
- Edit on iPhone, see changes in bot
- Full bidirectional sync

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
2. Note appears in Apple Notes "Tasks" folder
3. tasks.json file is created/updated

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
2. Note status changes to "✅ Done" in Apple Notes
3. tasks.json updated

### Test Sync
1. Open Apple Notes app
2. Edit a task note manually
3. Wait 5 minutes (or restart bot)
4. Send `#tasks` in WhatsApp
5. Should reflect your changes

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

### Apple Notes Not Working

**Error: "macOS required"**
- This bot only works on macOS
- Apple Notes uses macOS-specific JXA (JavaScript for Automation)

**Error: "osascript not found"**
- You're not on macOS
- osascript is built into macOS

**Error: "Folder 'Tasks' not found"**
- Don't worry! Bot auto-creates it on first task

**Permission Denied:**
1. System Settings → Privacy & Security → Automation
2. Find Terminal (or your terminal app)
3. Enable access to Notes

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

# Bot will recreate from Apple Notes on next sync
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

### Custom Notes Folder

Edit `apple_notes.py`:
```python
# Change the default folder
def get_client(folder='My Custom Folder') -> AppleNotesClient:
```

Or modify bot.js to pass folder name to Python scripts.

### Change Sync Interval

Edit `bot.js`:
```javascript
}, 5*60*1000);  // Change 5 to desired minutes
```

## 📊 Data Storage

### Apple Notes
- **Location**: Apple Notes app → "Tasks" folder
- **Format**: HTML notes with emoji and formatting
- **Sync**: Via iCloud across all your Apple devices
- **Backup**: Included in iCloud and Time Machine backups

### JSON Backup
- **Location**: `tasks.json` in project directory
- **Format**: JSON array of task objects
- **Purpose**: Fast reads, offline access, fallback if Notes unavailable
- **Backup**: Include in your own backup strategy

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

- **macOS only** - Requires Apple Notes (uses JXA)
- **Single user per bot** - One WhatsApp connection per bot instance
- **5-minute sync** - Not real-time (by design, to avoid excessive API calls)
- **Text only** - No image/file attachments (yet)
- **Simple search** - No full-text search (just list/filter)

### When to Upgrade

Consider more robust solution if you need:
- **>500 tasks** - SQLite would be faster
- **Multiple users** - Need proper database with permissions
- **Real-time sync** - Need websockets or polling
- **Complex queries** - Need SQL for joins/aggregations
- **Web UI** - Need Flask/React
- **Cross-platform** - Need Windows/Linux support

See [TODO.md](TODO.md) for planned features and workarounds.

## 🛠️ Development

### Project Structure

```
bot.js                  # Main task manager bot
├── WhatsAppBot()       # Initialize bot
├── runPython()         # Bridge to Python
├── createTask()        # Create via Apple Notes
├── getAllTasks()       # Read from Apple Notes
├── markTaskDone()      # Update in Apple Notes
├── parseTask()         # Parse WhatsApp messages
└── formatList()        # Format task lists

apple_notes.py          # Apple Notes integration
├── AppleNotesClient    # Main client class
├── _run_jxa()          # Execute JXA scripts
├── create_task()       # Create note
├── get_all_tasks()     # Read notes
└── mark_done()         # Update note

simple-whatsapp-bot/    # Reusable WhatsApp bot package
├── src/
│   └── WhatsAppBot.js  # Main bot class
├── examples/           # Usage examples
└── package.json
```

### Key Technologies

- **Node.js** - Main runtime for WhatsApp bot
- **whatsapp-web.js** - WhatsApp Web protocol (via Puppeteer)
- **Puppeteer** - Headless Chrome automation
- **Python 3** - Apple Notes integration
- **JXA** (JavaScript for Automation) - macOS scripting
- **child_process.spawn** - Bridge between Node.js and Python
- **JSON** - Data persistence

### Code Style

- **Simple > Clever** - Readable code over optimizations
- **Fail gracefully** - Degrade to JSON if Notes unavailable
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
- ✅ No database setup - Just Apple Notes
- ✅ No web server - Just Python script
- ✅ No deployment - Runs on your Mac
- ✅ No app install - Uses WhatsApp you already have
- ✅ No cloud costs - Everything local
- ✅ No learning curve - Natural conversation

### Perfect For

- Small families coordinating tasks
- Personal task tracking across devices
- Quick task capture from WhatsApp
- People who love Apple Notes
- Developers who want simple, hackable code

### Not For

- Large teams (no permissions/roles)
- Public/commercial use (no auth)
- Windows/Linux (macOS only)
- Mission-critical systems (no HA/redundancy)

## 🎉 Success Stories

Using this bot? Share your experience! Open an issue with tag `showcase`.

---

**Built with ❤️ for people who value simplicity over features**

*Questions? Check [TODO.md](TODO.md) for roadmap or open an issue!*
