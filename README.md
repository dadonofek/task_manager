# WhatsApp Task Manager Backend

A powerful task management backend designed to work seamlessly with WhatsApp. Now supports **automated message reading** or traditional manual mode.

## 🎯 Core Concept

- **WhatsApp = Your UI**: All communication happens in WhatsApp
- **Backend = Your Brain**: Stores tasks, handles deadlines, tracks progress
- **Automation = Optional**: Choose automated or manual mode

## ✨ Features

### Core Features
- ✅ Simple task creation from WhatsApp messages
- ✅ Task assignment and ownership tracking
- ✅ Flexible due date parsing (natural language)
- ✅ Multi-step workflow support
- ✅ Quick action URLs (mark done, reassign, update)
- ✅ Web views: /open, /mine, /today
- ✅ Task history tracking
- ✅ Free to host (Railway, Fly.io free tiers)

### NEW: Automated WhatsApp Integration
- 🤖 **Automatic message reading** from dedicated WhatsApp group
- 🤖 **Auto-reply** with task confirmation and quick action links
- 🤖 **Rate limiting** and quiet hours to reduce ban risk
- 🤖 **Session persistence** - QR code only needed once
- ⚠️ **WARNING**: May violate WhatsApp ToS - see [WHATSAPP_INTEGRATION.md](WHATSAPP_INTEGRATION.md)

### Integration Modes

| Mode | Description | Risk | Setup |
|------|-------------|------|-------|
| **Automated** | Bot reads messages from WhatsApp group | ⚠️ High ban risk | Medium |
| **Manual** | Traditional URL-based approach | ✅ Zero risk | Easy |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ (for automated mode only)
- SQLite (included with Python)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd task_manager

# Run setup script
./setup.sh

# Or manually:
pip install -r requirements.txt
npm install  # Only needed for automated mode
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```bash
   # Choose mode: 'automated' or 'manual'
   WHATSAPP_MODE=manual

   # Backend URL
   BASE_URL=http://localhost:5000

   # For automated mode:
   WHATSAPP_GROUP_NAME=My Tasks
   AUTO_REPLY_ENABLED=true
   MAX_TASKS_PER_HOUR=20
   QUIET_HOURS=23-07
   ```

3. **Customize users in `config.py`:**
   ```python
   USERS = ['Ofek', 'Wife']  # Add more users
   ```

### Running

**Option 1: Start everything together**
```bash
./start.sh
```

**Option 2: Start manually**
```bash
# Manual mode (Flask only)
python3 app.py

# Automated mode (both services)
python3 app.py  # Terminal 1
npm start       # Terminal 2
```

Server runs at: `http://localhost:5000`

## 📱 Usage

### Automated Mode

1. **Create WhatsApp group** named "My Tasks"
2. **Start services**: `./start.sh`
3. **Scan QR code** with WhatsApp
4. **Send message** to the group:
   ```
   #task
   Title: Buy groceries
   Owner: Wife
   Due: Today 6pm
   Next: Ofek picks up
   ```
5. **Receive auto-reply** with confirmation and quick action links!

### Manual Mode

1. **Compose task in WhatsApp**:
   ```
   #task
   Title: Upload medical docs
   Owner: Wife
   Due: Thu 20:00
   Next: Ofek submits
   ```

2. **Copy the message** and tap your keyboard shortcut

3. **Or visit URL**:
   ```
   https://yourapp.com/newTask?text=<paste-task-here>
   ```

4. **Save quick action links** from the response page

### Task Message Format

```
#task
Title: [Required] Task description
Owner: [Required] Person responsible (must be in USERS list)
Due: [Optional] Flexible format (Today 6pm, Thu 20:00, Jan 15)
Next: [Optional] Next step description
Notes: [Optional] Additional information
```

**Examples:**

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

```
#task
Title: Submit documents
Owner: Wife
Due: Friday 5pm
Next: Ofek reviews first
Notes: Passport and ID required
```

### Quick Actions

After creating a task, you'll receive quick action URLs:

- **View Task**: See all details
- **Mark Done**: Complete the task
- **Reassign**: Change owner (URLs for each user)
- **Update Due Date**: Modify deadline
- **Update Next Step**: Change next action

**Save these in WhatsApp as:**
- Starred messages
- Contacts with action URLs
- iPhone keyboard shortcuts

## 🔧 API Endpoints

### Task Management

#### Create Task
```http
POST /api/newTask
Content-Type: application/json

{
  "title": "Upload medical docs",
  "owner": "Wife",
  "due_date": "2024-01-15 20:00",
  "next_step": "Ofek submits",
  "notes": "Passport and ID"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": 15,
  "message": "Task #15 created successfully",
  "task": {
    "id": 15,
    "title": "Upload medical docs",
    "owner": "Wife",
    "due_date": "2024-01-15 20:00",
    "next_step": "Ofek submits",
    "status": "open",
    "created_at": "2024-01-15T10:30:00"
  },
  "quick_actions": {
    "mark_done": "https://yourapp.com/markDone/15",
    "view": "https://yourapp.com/task/15",
    "reassign": {
      "Ofek": "https://yourapp.com/reassign/15?to=Ofek",
      "Wife": "https://yourapp.com/reassign/15?to=Wife"
    }
  }
}
```

#### Get All Open Tasks
```http
GET /api/tasks?status=open
```

#### Get Tasks by Owner
```http
GET /api/tasks?owner=Ofek
```

#### Get Specific Task
```http
GET /api/task/15
```

#### Mark Task Done
```http
GET /markDone/15
POST /markDone/15
```

#### Reassign Task
```http
GET /reassign/15?to=Wife
POST /reassign/15
```

#### Update Due Date
```http
GET /updateDue/15?date=2024-01-20 15:00
```

#### Update Next Step
```http
GET /updateNext/15?step=Call doctor
```

### Web Views

- **All Open Tasks**: `/open`
- **My Tasks**: `/mine?owner=Ofek`
- **Today's Tasks**: `/today`
- **Single Task**: `/task/15`

## 📊 Database Schema

### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    owner TEXT NOT NULL,
    due_date TEXT,
    next_step TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    notes TEXT
);
```

### Task History Table
```sql
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY,
    task_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

## 🌐 Deployment

### Option 1: Railway (Free Tier)

1. Push code to GitHub
2. Connect to Railway
3. Set environment variables:
   ```
   BASE_URL=https://your-app.railway.app
   WHATSAPP_MODE=manual  # Start with manual
   ```
4. Deploy!

### Option 2: Fly.io (Free Tier)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Set secrets
fly secrets set BASE_URL=https://your-app.fly.dev
fly secrets set WHATSAPP_MODE=manual

# Deploy
fly deploy
```

### Option 3: VPS (for Automated Mode)

For automated mode, you need a VPS that can run both Python and Node.js:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip nodejs npm

# Install Chrome (for whatsapp-web.js)
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update
sudo apt-get install google-chrome-stable

# Clone and setup
git clone <your-repo-url>
cd task_manager
./setup.sh

# Start with PM2 (process manager)
npm install -g pm2
pm2 start start.sh --name whatsapp-task-manager
pm2 save
pm2 startup
```

## ⚠️ WhatsApp Integration Warnings

### Automated Mode Risks

**Using whatsapp-web.js violates WhatsApp Terms of Service and may result in permanent account ban.**

**Before using automated mode:**
- ✅ Read [WHATSAPP_INTEGRATION.md](WHATSAPP_INTEGRATION.md) thoroughly
- ✅ Understand the ban risk
- ✅ Use a secondary phone number if possible
- ✅ Start with manual mode to test
- ✅ Monitor only ONE dedicated group
- ✅ Enable rate limiting and quiet hours
- ✅ Have a backup plan

**Recommended approach:**
1. Start with **manual mode** (zero risk)
2. Test thoroughly with your family
3. If you need automation, use a **secondary number**
4. Create a **dedicated group** for tasks only
5. Configure **rate limits** and **quiet hours**
6. Be prepared to switch back to manual if banned

### Manual Mode (Safest)

- ✅ **Zero ban risk** - no automation
- ✅ **Simple setup** - Flask only
- ✅ **Works everywhere** - any phone, any platform
- ❌ Requires manual copy/paste
- ❌ Extra step to create tasks

## 📖 Architecture

### Automated Mode
```
┌─────────────────────────────────┐
│  WhatsApp Group "My Tasks"      │
│  (Send #task messages)          │
└────────────┬────────────────────┘
             │
             │ Auto-detect
             ↓
┌─────────────────────────────────┐
│  WhatsApp Bot (whatsapp-web.js) │
│  • Monitors group               │
│  • Parses #task format          │
│  • Creates tasks via API        │
│  • Replies with links           │
└────────────┬────────────────────┘
             │
             │ HTTP POST
             ↓
┌─────────────────────────────────┐
│  Flask Backend                  │
│  • Task CRUD operations         │
│  • Quick action URLs            │
│  • Web views                    │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  SQLite Database                │
│  • Tasks table                  │
│  • Task history table           │
└─────────────────────────────────┘
```

### Manual Mode
```
┌─────────────────────────────────┐
│  WhatsApp (Compose #task)       │
└────────────┬────────────────────┘
             │
             │ Manual: copy → paste → URL
             ↓
┌─────────────────────────────────┐
│  Flask Backend                  │
│  • Parse WhatsApp format        │
│  • Create task                  │
│  • Generate quick action URLs   │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  SQLite Database                │
└─────────────────────────────────┘
```

## 🎨 Customization

### Add More Users

Edit `config.py`:
```python
USERS = ['Ofek', 'Wife', 'Mom', 'Brother', 'Friend']
```

### Change WhatsApp Format

Edit `parse_whatsapp_task()` in `app.py` to match your preferred format.

### Add Email Reminders

1. Install email library: `pip install flask-mail`
2. Create `/api/send-reminders` endpoint
3. Set up cron job:
   ```bash
   0 8 * * * curl https://yourapp.com/api/send-reminders
   ```

### Custom Quick Actions

Add new routes in `app.py`:
```python
@app.route('/snooze/<int:task_id>')
def snooze_task(task_id):
    # Snooze logic here
    pass
```

## 🔒 Security Notes

- **No authentication by default** - Add auth if hosting publicly
- **SQLite limitations** - Single concurrent user (upgrade to PostgreSQL for production)
- **Use HTTPS in production** - Free with Railway/Fly.io
- **Change SECRET_KEY** - Set strong secret in production
- **Automated mode risks** - Account ban possible

## 🛠️ Development

### Run in Debug Mode
```bash
export DEBUG=true
python app.py
```

### Database Management

```bash
# View database
sqlite3 tasks.db

# Show all tasks
sqlite3 tasks.db "SELECT * FROM tasks;"

# Show task history
sqlite3 tasks.db "SELECT * FROM task_history;"

# Reset database
rm tasks.db
python -c "from database import init_db; init_db()"
```

### Testing

```bash
# Test API endpoint
curl -X POST http://localhost:5000/api/newTask \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "owner": "Ofek"}'

# Test quick action
curl http://localhost:5000/markDone/1
```

## 📚 Documentation

- **[WHATSAPP_INTEGRATION.md](WHATSAPP_INTEGRATION.md)** - Comprehensive WhatsApp integration guide
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world usage examples

## 🎯 Why This Works

### For Automated Mode
1. **Seamless experience**: Never leave WhatsApp
2. **Instant feedback**: Auto-replies with confirmation
3. **Zero friction**: Just send a message
4. **Family-friendly**: Everyone stays in WhatsApp
5. **Structured data**: Backend tracks everything properly

### For Manual Mode
1. **Zero WhatsApp API costs**: No bot, no automation, no fees
2. **Zero ban risk**: Completely safe
3. **Structured data**: Backend tracks everything properly
4. **Automatic reminders**: Backend can schedule notifications (future feature)
5. **Always accessible**: Check /open anytime from any device

## 🚀 Getting Started Checklist

- [ ] Run `./setup.sh`
- [ ] Choose your mode in `.env` (start with manual!)
- [ ] Add users in `config.py`
- [ ] Start services: `./start.sh`
- [ ] (Automated mode) Create WhatsApp group "My Tasks"
- [ ] (Automated mode) Scan QR code
- [ ] Send test message with #task format
- [ ] Save quick action links
- [ ] Deploy to production (Railway/Fly.io)
- [ ] Set up keyboard shortcuts (manual mode)
- [ ] Enjoy organized task management!

## 🤝 Contributing

Pull requests welcome! Please test thoroughly.

## 📄 License

MIT License - Use freely!

## 💬 Support

- **Issues?** Open a GitHub issue
- **Questions?** Read the documentation
- **WhatsApp integration help?** See [WHATSAPP_INTEGRATION.md](WHATSAPP_INTEGRATION.md)

---

## 📋 Project Structure

```
task_manager/
├── app.py                      # Flask application (main backend)
├── models.py                   # Task model & database operations
├── database.py                 # SQLite setup & connection
├── config.py                   # Configuration management
├── whatsapp_bot.js            # WhatsApp automation (NEW!)
├── package.json               # Node.js dependencies (NEW!)
├── .env.example               # Environment template (NEW!)
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script (NEW!)
├── start.sh                   # Start script (NEW!)
├── Procfile                   # Deployment configuration
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Main layout
│   ├── open.html             # All open tasks view
│   ├── mine.html             # Tasks by owner
│   ├── today.html            # Due today tasks
│   ├── task.html             # Single task detail
│   ├── task_created.html     # Task creation confirmation
│   └── action_success.html   # Action confirmation
├── README.md                  # This file
├── WHATSAPP_INTEGRATION.md    # WhatsApp setup guide (NEW!)
├── QUICKSTART.md             # Quick start guide
├── EXAMPLES.md               # Usage examples
└── test_basic.py             # Basic tests

## 🎓 Key Differences: Automated vs Manual

| Aspect | Automated Mode | Manual Mode |
|--------|---------------|-------------|
| **Message Reading** | Automatic | Manual copy/paste |
| **Task Creation** | Send message → Done | Send message → Copy → Open URL |
| **Auto-Reply** | Yes (with links) | No |
| **Setup** | Flask + Node.js + WhatsApp login | Flask only |
| **Ban Risk** | ⚠️ **HIGH** | ✅ None |
| **Best For** | Tech-savvy users with secondary number | Everyone, production use |
| **Dependencies** | Python + Node.js + Chrome/Chromium | Python only |
| **Server Requirements** | Always-on VPS | Any Python host |

---

**Made with ❤️ for WhatsApp-first task management**

**Start with manual mode, upgrade to automated only if you accept the risks!**
