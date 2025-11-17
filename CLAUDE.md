# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WhatsApp Task Manager Backend - A lightweight Flask application that enables task management through WhatsApp using quick action URLs. No WhatsApp bot or API required - users manually tap links to sync tasks between WhatsApp and the backend.

**Core workflow:**
1. User writes task in WhatsApp using `#task` format
2. User manually taps a quick action URL (saved as keyboard shortcut)
3. Backend creates task and returns action links
4. User taps links in WhatsApp to mark done, reassign, etc.

## Development Commands

### Run the application
```bash
python app.py
```
Server starts at `http://localhost:5000`

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

**Four-layer structure:**

1. **app.py** - Flask routes and request handling
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
   - `USERS` - list of valid task owners

**Data flow:**
- Routes in `app.py` handle HTTP requests
- Routes call static methods on `Task` model
- `Task` methods use `get_db()` context manager from `database.py`
- All updates logged to `task_history` table automatically

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

## Database Schema

**tasks table:**
- `id` - Primary key
- `title`, `owner`, `due_date`, `next_step`, `notes` - Task fields
- `status` - 'open' or 'done'
- `created_at`, `completed_at` - Timestamps

**task_history table:**
- Tracks all actions: 'created', 'completed', 'reassigned', 'due_date_changed', 'next_step_updated'

## Configuration

Set these environment variables for deployment:
- `BASE_URL` - Your production URL (e.g., `https://yourapp.railway.app`)
- `SECRET_KEY` - Strong secret for Flask sessions in production
- `DEBUG` - Set to 'true' for debug mode
- `DATABASE_PATH` - Custom database location (defaults to `tasks.db`)

Edit `config.py` to add more users to the `USERS` list.

## Templates

HTML templates in `templates/` directory use Flask's Jinja2 templating:
- `base.html` - Base template with common styling
- `open.html`, `mine.html`, `today.html` - Task list views
- `task.html` - Single task view with quick action buttons
- `task_created.html` - Confirmation page after task creation
- `action_success.html` - Generic success page for quick actions
