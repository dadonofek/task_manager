# WhatsApp Task Manager

Manage tasks directly from your WhatsApp group. No manual links - just chat naturally with a bot that handles everything.

## 🎯 What Is This?

A task manager where you create, view, and complete tasks entirely through WhatsApp messages. The bot reads your messages, creates tasks, and lets you tap quick action links.

**Perfect for families and small teams.**

## ✨ Features

- 🤖 **WhatsApp Bot** - Auto-reads messages, creates tasks, replies with action links
- 🎯 **Priority Levels** - High 🔴, Medium 🟡, Low 🟢 (auto-sorted)
- 🏷️ **Categories** - Tag tasks: work, home, shopping, etc.
- 👥 **Multi-User** - Assign to Ofek, Shachar, or anyone
- 📅 **Due Dates** - Flexible date parsing
- 🌐 **Web View** - Browse tasks at http://localhost:5001
- 📱 **Quick Actions** - Tap links to mark done or reassign

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.8+
- Node.js 14+
- WhatsApp on your phone

### 1. Install
```bash
git clone <your-repo>
cd task_manager

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies
npm install
```

### 2. Configure
Create a WhatsApp group called "Task Manager" (or rename yours)

Edit `config.py` if needed:
```python
USERS = ['Ofek', 'Shachar']  # Your names
WHATSAPP_GROUP_NAME = 'Task Manager'  # Your group name
```

### 3. Run
```bash
./start.sh
```

This starts:
- Flask backend on port 5001
- WhatsApp bot (shows QR code)

### 4. Authenticate
1. QR code appears in terminal
2. Open WhatsApp → Settings → Linked Devices → Link a Device
3. Scan the QR code
4. Done! Bot is now connected

### 5. Test
In your WhatsApp group, send:
```
#help
```

Bot should reply with commands! 🎉

## 📱 Using the Bot

### Create a Task
```
#task
Title: Buy groceries
Owner: Ofek
Priority: high
Category: shopping
Due: Tomorrow 6pm
```

Bot replies with:
```
✅ Task #1 Created!

📋 Buy groceries
👤 Ofek
🔴 Priority: high
🏷️ Category: shopping
⏰ Due: Tomorrow 6pm

Quick Actions:
✅ Mark Done: [link]
👥 Reassign: [links]
```

### List Tasks
- `#tasks` or `#list` - All open tasks
- `#my` - Your tasks
- `#my Shachar` - Shachar's tasks

### Quick Actions
Tap links in bot messages to:
- ✅ Mark task done
- 👥 Reassign to someone
- 🔗 View full details

## 🎯 Priority Levels

| Priority | When to Use |
|----------|-------------|
| 🔴 **high** | Urgent, deadline today/tomorrow |
| 🟡 **medium** | Normal tasks (default) |
| 🟢 **low** | Can wait, nice-to-have |

Tasks are automatically sorted: high → medium → low → due date

## 🏷️ Categories

Use any category you want:
- `work`, `home`, `shopping`, `personal`, `finance`, `health`

Categories help filter and organize. Create your own!

## 🌐 Web Interface

Browse tasks in your browser:
- **All Open**: http://localhost:5001/open
- **My Tasks**: http://localhost:5001/mine?owner=Ofek
- **Due Today**: http://localhost:5001/today
- **Specific Task**: http://localhost:5001/task/1

## 🔧 Configuration

### Add More Users
Edit `config.py`:
```python
USERS = ['Ofek', 'Shachar', 'Mom', 'Dad']
```

### Change Group Name
Edit `config.py`:
```python
WHATSAPP_GROUP_NAME = 'Family Tasks'
```

Or set environment variable:
```bash
export WHATSAPP_GROUP_NAME="Family Tasks"
```

### Change Port
Edit `start.sh` or set:
```bash
export BASE_URL="http://localhost:5002"
```

## 📖 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete user guide with examples
- **[FEATURES.md](FEATURES.md)** - Technical feature documentation
- **[WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)** - Detailed WhatsApp setup
- **[TODO.md](TODO.md)** - Upcoming features and ideas
- **[CLAUDE.md](CLAUDE.md)** - Developer/architecture notes

## 🧪 Testing

### Run Tests
```bash
# Basic tests
python test_basic.py

# Advanced tests (priority, category)
python test_advanced.py
```

All tests should pass!

### Test the Bot
In WhatsApp:
```
#task
Title: Test task
Owner: Ofek
Priority: high
Category: test
```

Check if bot replies with task creation confirmation.

## 🔧 Troubleshooting

### Bot Not Responding
1. Check Flask is running: `curl http://localhost:5001/health`
2. Check group name matches config
3. Restart: `Ctrl+C` then `./start.sh`

### QR Code Won't Scan
- Terminal window too small? Resize it
- QR code cut off? Scroll up
- Wrong WhatsApp app? Use phone, not web/desktop

### Port Already in Use
On macOS, disable AirPlay Receiver:
System Settings → General → AirDrop & Handoff → Turn off AirPlay Receiver

Or change port in `start.sh`

### Authentication Lost
If bot stops working:
```bash
rm -rf .wwebjs_auth
./start.sh
```
Scan QR code again.

## 🗄️ Database

### View Database
```bash
sqlite3 tasks.db
SELECT * FROM tasks WHERE status='open';
```

### Reset Database
```bash
rm tasks.db
python -c "from database import init_db; init_db()"
```

### Migrate Existing Database
If you have old database without priority/category:
```bash
python migrate_db.py
```

## 🚀 Deployment (Optional)

Currently designed for local use. For remote deployment:

1. Deploy Flask to Railway/Render/Fly.io
2. Run WhatsApp bot on always-on machine (home server, VPS)
3. Update `BASE_URL` in config
4. Add authentication (not included)

**Note**: WhatsApp bot needs to stay connected, so needs an always-on server.

## 🏗️ Architecture

```
WhatsApp Group
     ↓
WhatsApp Bot (Node.js)
     ↓ HTTP API
Flask Backend (Python)
     ↓
SQLite Database
     ↓
Web Interface (HTML)
```

## 🔒 Security

⚠️ **This is designed for personal/family use**

Before public deployment:
- Add user authentication
- Use HTTPS only
- Rate limit API endpoints
- Use PostgreSQL instead of SQLite
- Validate all inputs
- Set strong SECRET_KEY

## 📊 Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **WhatsApp**: whatsapp-web.js (Node.js)
- **Testing**: Python unittest
- **Frontend**: HTML/CSS (Jinja2 templates)

## 🎯 Why This Works

1. **Zero API Costs** - Uses WhatsApp Web protocol
2. **No App Required** - Works with regular WhatsApp
3. **Simple** - Natural conversation, not commands
4. **Reliable** - Bot handles parsing and responses
5. **Flexible** - Priorities, categories, due dates
6. **Accessible** - WhatsApp + web interface

## 📝 Example Workflow

**Morning:**
```
You: #tasks
Bot: [Lists all open tasks sorted by priority]
```

**Create Urgent Task:**
```
You: #task
     Title: Fix production bug
     Owner: Ofek
     Priority: high
     Category: work
     Due: Today 5pm

Bot: ✅ Task #42 created! [Quick action links]
```

**Complete Task:**
```
You: [Tap "Mark Done" link]
Bot: ✅ Task #42 marked as done!
```

**Check Status:**
```
You: #my
Bot: [Lists your tasks]
```

## 🤝 Contributing

Pull requests welcome! Please:
1. Run tests: `python test_basic.py && python test_advanced.py`
2. Update documentation
3. Use small commits

## 📄 License

MIT License - Free to use and modify!

## 💡 Tips

1. **Set Priority** - Helps focus on what matters
2. **Use Categories** - Easier to find related tasks
3. **Review Daily** - Check `#tasks` every morning
4. **Mark Done** - Keep list clean and current
5. **Share Load** - Assign tasks fairly

## 🆘 Need Help?

1. **Quick Help**: Send `#help` in WhatsApp
2. **User Guide**: Read [USAGE_GUIDE.md](USAGE_GUIDE.md)
3. **Setup Issues**: Check [WHATSAPP_SETUP.md](WHATSAPP_SETUP.md)
4. **GitHub Issues**: Report bugs and request features

---

**Built with ❤️ for families who want simple, effective task management**
