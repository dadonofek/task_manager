# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WhatsApp Task Manager - A task management system with WhatsApp group integration. Users can create and manage tasks directly from a WhatsApp group using a bot.

**Core workflow (with WhatsApp bot):**
1. User sends `#task` message in WhatsApp group
2. WhatsApp bot reads message and calls Flask API
3. Bot replies with task confirmation and quick action links
4. User taps links to mark done, reassign, etc.

**Alternative workflow (manual):**
1. User writes task in WhatsApp using `#task` format
2. User manually taps a quick action URL (saved as keyboard shortcut)
3. Backend creates task and returns action links
4. User taps links in WhatsApp to mark done, reassign, etc.

## Development Commands

### Run the application

**With WhatsApp bot (recommended):**
```bash
./start.sh
```
Starts both Flask (port 5001) and WhatsApp bot. First time: scan QR code.

**Flask only:**
```bash
python app.py
```
Server starts at `http://localhost:5001`

**WhatsApp bot only:**
```bash
node whatsapp_bot.js
```
Requires Flask to be running on port 5001.

### Run tests
```bash
python test_basic.py
```

### Database management
```bash
# View database
sqlite3 tasks.db

# Reset database
rm tasks.db
python -c "from database import init_db; init_db()"
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Architecture

**Five-layer structure:**

1. **whatsapp_bot.js** - WhatsApp integration (Node.js)
   - Connects to WhatsApp Web using `whatsapp-web.js`
   - Monitors specified WhatsApp group for messages
   - Parses `#task`, `#list`, `#my`, `#help` commands
   - Calls Flask API to create/retrieve tasks
   - Sends formatted replies with quick action links
   - Stores authentication in `.wwebjs_auth/` directory

2. **app.py** - Flask routes and request handling
   - Web UI routes: `/open`, `/mine`, `/today`, `/task/<id>`
   - Quick action routes: `/markDone/<id>`, `/reassign/<id>`, `/updateDue/<id>`, `/updateNext/<id>`
   - API routes: `/api/newTask`, `/api/tasks`, `/api/task/<id>`
   - WhatsApp text parsing: `parse_whatsapp_task()` expects format like `Title: X\nOwner: Y\nDue: Z`

2. **models.py** - Task model with static methods for all operations
   - All database operations go through `Task` class (no direct DB access in routes)
   - Methods: `create()`, `get_by_id()`, `get_all_open()`, `get_by_owner()`, `get_today()`, `mark_done()`, `reassign()`, `update_due_date()`, `update_next_step()`
   - Automatically logs actions to `task_history` table

3. **database.py** - SQLite setup and connection management
   - `init_db()` creates tables if they don't exist
   - `get_db()` context manager for connections
   - `add_task_history()` logs all task changes

4. **config.py** - Configuration via environment variables
   - `BASE_URL` - deployed URL for quick action links
   - `DATABASE_PATH` - SQLite file location
   - `USERS` - list of valid task owners (currently: Ofek, Shachar)
   - `WHATSAPP_GROUP_NAME` - name of WhatsApp group to monitor
   - `WHATSAPP_ENABLED` - enable/disable WhatsApp bot

5. **start.sh** - Startup script
   - Checks dependencies (Node.js, Python)
   - Installs npm packages if needed
   - Starts Flask backend in background
   - Starts WhatsApp bot in foreground
   - Handles graceful shutdown

**Data flow:**
- WhatsApp group messages → whatsapp_bot.js → Flask API → Database
- Routes in `app.py` handle HTTP requests (from bot and web UI)
- Routes call static methods on `Task` model
- `Task` methods use `get_db()` context manager from `database.py`
- All updates logged to `task_history` table automatically
- Bot receives API response → formats message → sends to WhatsApp group

## Key Design Patterns

**WhatsApp text parsing:** The `parse_whatsapp_task()` function (app.py:17) expects this format:
```
#task
Title: Task title
Owner: Person name
Due: Thu 20:00
Next: Next step description
```

**Date parsing:** Uses `python-dateutil` to flexibly parse dates like "Thu 20:00", "Jan 15 8pm", "2024-01-15 20:00"

**Quick actions:** Routes like `/markDone/<id>` work with both GET (returns HTML) and POST (returns JSON) for flexibility

**Task history:** Every task modification automatically creates a history entry via `add_task_history()` (database.py:52)

**No authentication:** This is designed for personal/family use. Add auth before public deployment.

## WhatsApp Bot Commands

The bot (whatsapp_bot.js) recognizes these commands in the configured WhatsApp group:

**Create Task:**
```
#task
Title: Buy groceries
Owner: Ofek
Due: Tomorrow 6pm
Next: Make shopping list
```

**List Tasks:**
- `#tasks` or `#list` - Show all open tasks
- `#my` - Show your tasks
- `#my Shachar` - Show Shachar's tasks

**Help:**
- `#help` or `#?` - Show help message with all commands

**Bot responses:**
- Task created: Confirmation + quick action links
- Task list: Formatted list with task details
- Errors: Helpful error messages with correct format examples

## Database Schema

**tasks table:**
- `id` - Primary key
- `title`, `owner`, `due_date`, `next_step`, `notes` - Task fields
- `status` - 'open' or 'done'
- `created_at`, `completed_at` - Timestamps

**task_history table:**
- Tracks all actions: 'created', 'completed', 'reassigned', 'due_date_changed', 'next_step_updated'

## Configuration

### Environment Variables

Set these environment variables (use `.env` file or export):

**Flask:**
- `BASE_URL` - Your production URL (e.g., `https://yourapp.railway.app`)
- `SECRET_KEY` - Strong secret for Flask sessions in production
- `DEBUG` - Set to 'true' for debug mode
- `DATABASE_PATH` - Custom database location (defaults to `tasks.db`)

**WhatsApp Bot:**
- `WHATSAPP_GROUP_NAME` - Name of WhatsApp group to monitor (default: "Task Manager")
- `WHATSAPP_ENABLED` - Set to 'true' to enable bot
- `FLASK_API_URL` - Flask API URL (default: http://localhost:5001)

### User Configuration

Edit `config.py` to customize users:
```python
USERS = ['Ofek', 'Shachar']  # Add/remove users as needed
```

User names appear in:
- Navigation menu (Ofek's Tasks, Shachar's Tasks)
- Task assignment options
- Quick action reassign links

### WhatsApp Setup

See `WHATSAPP_SETUP.md` for detailed setup instructions:
1. Install Node.js dependencies: `npm install`
2. Configure group name: Set `WHATSAPP_GROUP_NAME` environment variable
3. Run: `./start.sh`
4. Scan QR code with WhatsApp on your phone
5. Send `#help` in your group to test

## Templates

HTML templates in `templates/` directory use Flask's Jinja2 templating:
- `base.html` - Base template with common styling
- `open.html`, `mine.html`, `today.html` - Task list views
- `task.html` - Single task view with quick action buttons
- `task_created.html` - Confirmation page after task creation
- `action_success.html` - Generic success page for quick actions
