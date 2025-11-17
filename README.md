# WhatsApp Task Manager Backend

A lightweight task management backend designed to work seamlessly with WhatsApp as the primary interface. No WhatsApp bot required - completely free!

## 🎯 Core Concept

- **WhatsApp = Your UI**: All communication happens in WhatsApp
- **Backend = Your Brain**: Stores tasks, handles deadlines, sends reminders
- **Quick Actions = The Bridge**: Tap links to sync WhatsApp with backend

## ✨ Features

- ✅ Simple task creation from WhatsApp messages
- ✅ Task assignment and ownership tracking
- ✅ Due date management
- ✅ Multi-step workflow support
- ✅ Quick action URLs (mark done, reassign, update)
- ✅ Web views: /open, /mine, /today
- ✅ Zero WhatsApp API costs (no bot needed!)
- ✅ Free to host (Railway, Fly.io free tiers)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd task_manager

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The server will start at `http://localhost:5000`

### Configuration

Edit `config.py` to customize:

```python
BASE_URL = 'https://your-domain.com'  # Your production URL
USERS = ['Ofek', 'Wife']  # Add more users
```

## 📱 How to Use

### 1. Creating Tasks in WhatsApp

In your WhatsApp chat, write a task message:

```
#task
Title: Upload medical docs
Owner: Wife
Due: Thu 20:00
Next: Ofek submits
```

Then:
1. Copy the task text
2. Tap your saved shortcut: "Create Task"
3. Or visit: `https://yourapp.com/newTask?text=<paste here>`

The backend creates the task and gives you quick action links!

### 2. Quick Actions

Save these URL patterns as iPhone keyboard shortcuts or WhatsApp starred messages:

**Mark Done:**
```
https://yourapp.com/markDone/14
```

**Reassign:**
```
https://yourapp.com/reassign/14?to=Ofek
```

**Update Due Date:**
```
https://yourapp.com/updateDue/14?date=Fri 10:00
```

### 3. Viewing Tasks

Open these URLs anytime:

- **All Open Tasks**: `https://yourapp.com/open`
- **My Tasks**: `https://yourapp.com/mine?owner=Ofek`
- **Today's Tasks**: `https://yourapp.com/today`
- **Specific Task**: `https://yourapp.com/task/14`

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
GET /api/task/14
```

#### Mark Task Done
```http
GET /markDone/14
POST /markDone/14
```

#### Reassign Task
```http
GET /reassign/14?to=Wife
POST /reassign/14
```

#### Update Due Date
```http
GET /updateDue/14?date=2024-01-20 15:00
```

#### Update Next Step
```http
GET /updateNext/14?step=Call doctor
```

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
    timestamp TEXT NOT NULL
);
```

## 🌐 Deployment

### Option 1: Railway (Free Tier)

1. Push code to GitHub
2. Connect to Railway
3. Set environment variable: `BASE_URL=https://your-app.railway.app`
4. Deploy!

### Option 2: Fly.io (Free Tier)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Set secrets
fly secrets set BASE_URL=https://your-app.fly.dev

# Deploy
fly deploy
```

### Option 3: Any Python Host

Requirements:
- Python 3.8+
- SQLite support
- 256MB RAM minimum

## 📝 WhatsApp Workflow Examples

### Example 1: Creating and Completing a Task

**In WhatsApp:**
```
You: #task
     Title: Buy groceries
     Owner: Wife
     Due: Today 6pm
     Next: Ofek picks up

[Tap "Create Task" shortcut]

Backend: ✅ Task #15 created!
         Quick actions: [links]

Wife: Done!

You: [Tap "Mark Done #15"]

Backend: ✅ Task #15 marked as done!
```

### Example 2: Reassigning a Task

**In WhatsApp:**
```
You: Can you handle the medical docs?

Wife: Sure!

You: [Tap "Reassign #14 to Wife"]

Backend: ✅ Task #14 reassigned to Wife!
```

### Example 3: Checking Your Tasks

**In WhatsApp:**
```
You: [Tap "My Tasks"]

Browser opens: Shows all tasks assigned to you
```

## 🎨 Customization

### Add More Users

Edit `config.py`:
```python
USERS = ['Ofek', 'Wife', 'Mom', 'Brother']
```

### Change WhatsApp Format

Edit the `parse_whatsapp_task()` function in `app.py` to match your preferred format.

### Add Email Reminders

Install a cron job:
```bash
# Run daily at 8am
0 8 * * * curl https://yourapp.com/api/send-reminders
```

Then implement `/api/send-reminders` endpoint to email overdue tasks.

## 🔒 Security Notes

- No authentication by default (add if hosting publicly)
- SQLite is single-user (upgrade to PostgreSQL for concurrent access)
- Use HTTPS in production
- Set strong SECRET_KEY in production

## 🛠️ Development

### Run in Debug Mode
```bash
export DEBUG=true
python app.py
```

### Run Tests
```bash
# Coming soon!
pytest tests/
```

### Database Management

```bash
# View database
sqlite3 tasks.db

# Reset database
rm tasks.db
python -c "from database import init_db; init_db()"
```

## 📖 Architecture

```
WhatsApp (UI)
    ↓ (manual: tap quick action link)
Flask Backend (Logic)
    ↓
SQLite Database (Storage)
    ↓
Web Views (Visibility)
```

## 🎯 Why This Works

1. **Zero WhatsApp API costs**: No bot, no automation, no fees
2. **Zero friction**: Wife never leaves WhatsApp
3. **Structured data**: Backend tracks everything properly
4. **Automatic reminders**: Backend can schedule notifications
5. **Always accessible**: Check /open anytime from any device

## 🚀 Next Steps

1. **Deploy to Railway/Fly.io**
2. **Set up keyboard shortcuts** on iPhone
3. **Create first task** in WhatsApp
4. **Tap quick action** to sync
5. **Enjoy organized task management!**

## 📄 License

MIT License - Use freely!

## 🤝 Contributing

Pull requests welcome! Please test thoroughly.

## 💬 Support

Questions? Open an issue on GitHub!

---

**Made with ❤️ for WhatsApp-first task management**
