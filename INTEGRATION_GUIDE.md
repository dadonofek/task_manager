# WhatsApp & Apple Notes Integration Guide

This guide explains how to use the WhatsApp (Twilio) and Apple Notes integrations with your Task Manager.

## Overview

This implementation provides a **pragmatic middle ground** architecture:

- **WhatsApp** = Quick capture and updates when you're mobile or want to fire off a task without ceremony. The friction is nearly zero.
- **Apple Notes** = The "source of truth" where you can see the full landscape, organize, plan, and understand context at a glance.

## WhatsApp Integration (Twilio)

### Prerequisites

1. **Twilio Account**: Sign up at https://www.twilio.com
2. **WhatsApp Sandbox**: Join the Twilio WhatsApp Sandbox for testing
3. **Credentials**: Get your Account SID and Auth Token from the Twilio Console

### Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Set Environment Variables

```bash
export TWILIO_ACCOUNT_SID='your_account_sid'
export TWILIO_AUTH_TOKEN='your_auth_token'
export TWILIO_WHATSAPP_NUMBER='whatsapp:+14155238886'  # Sandbox number
```

Or create a `.env` file:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

#### 3. Join the WhatsApp Sandbox

1. Go to Twilio Console → WhatsApp → Sandbox
2. Send the join message to the sandbox number from your WhatsApp
3. Example: Send "join YOUR-SANDBOX-KEYWORD" to +1 415 523 8886

#### 4. Configure Webhook URL

1. Start your Flask app (or deploy it publicly)
2. If testing locally, use ngrok to expose your local server:
   ```bash
   ngrok http 5000
   ```
3. In Twilio Console → WhatsApp → Sandbox Settings:
   - Set "When a message comes in" to: `https://your-domain.com/whatsapp/webhook`
   - Or with ngrok: `https://abc123.ngrok.io/whatsapp/webhook`

### Usage

#### Sending Messages via WhatsApp

**Create a Task:**
```
#task
Title: Upload medical docs
Owner: Wife
Due: Thu 20:00
Next: Ofek submits
```

**View Your Tasks:**
```
my tasks
```

**View Today's Tasks:**
```
today
```

**Get Help:**
```
help
```

#### Sending Messages Programmatically

**Using Python:**

```python
from whatsapp_integration import WhatsAppClient

# Initialize client
client = WhatsAppClient()

# Send a simple message
result = client.send_message(
    to_number='+1234567890',
    body='Hello from Task Manager!'
)

# Send a task notification
task = {
    'id': 1,
    'title': 'Review documents',
    'owner': 'Ofek',
    'due_date': '2024-01-15 20:00',
    'status': 'open'
}

action_urls = {
    'mark_done': 'https://example.com/markDone/1',
    'view_task': 'https://example.com/task/1'
}

result = client.send_task_notification(
    to_number='+1234567890',
    task=task,
    action_urls=action_urls
)
```

**Using API Endpoint:**

```bash
# Send a message
curl -X POST http://localhost:5000/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "body": "Your message here"
  }'

# Send task notification
curl -X POST http://localhost:5000/whatsapp/notify/1 \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890"}'
```

### API Endpoints

- `POST /whatsapp/webhook` - Receives incoming WhatsApp messages (Twilio webhook)
- `POST /whatsapp/send` - Send a WhatsApp message programmatically
- `POST /whatsapp/notify/<task_id>` - Send a task notification via WhatsApp

---

## Apple Notes Integration

### Prerequisites

1. **macOS**: This integration only works on macOS with Apple Notes installed
2. **Python 3.6+**: Already required for the Flask app
3. **Apple Notes App**: Must be installed and configured

### Setup

No additional setup required! The integration uses JavaScript for Automation (JXA) via `osascript`, which is built into macOS.

### Usage

#### Using Python

```python
from apple_notes_integration import AppleNotesClient

# Initialize client
client = AppleNotesClient()

# Create a note
note = client.create_note(
    title='My Task',
    body='Task description here',
    folder='Tasks'
)

# Get all notes
notes = client.get_all_notes()

# Get notes from specific folder
tasks = client.get_all_notes(folder='Tasks')

# Find notes by title
matching_notes = client.find_notes_by_title('medical')

# Update a note
client.update_note(note_id='some-id', new_body='Updated content')

# Delete a note
client.delete_note(note_id='some-id')
```

#### Syncing Tasks to Apple Notes

```python
from apple_notes_integration import AppleNotesClient
from models import Task

# Get all open tasks
tasks = Task.get_all_open()

# Sync to Apple Notes
client = AppleNotesClient()
stats = client.sync_tasks_to_notes(
    tasks=[task.to_dict() for task in tasks],
    folder='Tasks',
    clear_existing=True  # Optional: clear existing task notes first
)

print(f"Created {stats['created']} notes, {stats['errors']} errors")
```

#### Create Task Note with Formatting

```python
from apple_notes_integration import AppleNotesClient

client = AppleNotesClient()

task = {
    'id': 1,
    'title': 'Upload documents',
    'owner': 'Ofek',
    'due_date': '2024-01-15 20:00',
    'next_step': 'Scan documents',
    'status': 'open',
    'notes': 'Important client meeting prep'
}

# Creates a nicely formatted note in Apple Notes
note = client.create_task_note(task, folder='Tasks')
```

### Available Methods

#### `AppleNotesClient` Methods:

- `get_all_folders()` - List all folders/accounts
- `get_default_folder()` - Get default folder name
- `create_note(title, body, folder=None)` - Create a new note
- `get_all_notes(folder=None)` - Get all notes (optionally filtered by folder)
- `find_notes_by_title(title)` - Search notes by title
- `get_note_by_id(note_id)` - Get specific note
- `update_note(note_id, new_body)` - Update note content
- `delete_note(note_id)` - Delete a note
- `create_task_note(task, folder='Tasks')` - Create formatted task note
- `sync_tasks_to_notes(tasks, folder='Tasks', clear_existing=False)` - Sync multiple tasks

---

## Sync Architecture

### The Pragmatic Middle Ground

This implementation lets each interface do what it's best at:

**WhatsApp Strengths:**
- Zero-friction task capture when mobile
- Quick status queries ("my tasks", "today")
- Instant notifications
- No app switching required

**Apple Notes Strengths:**
- Visual task landscape
- Rich formatting and organization
- Full-text search
- Planning and context review
- Works offline

### Sync Strategy

**Option 1: Manual Sync (Simple)**

```python
# Run this periodically or on-demand
from apple_notes_integration import sync_tasks_to_apple_notes
from models import Task

tasks = Task.get_all_open()
stats = sync_tasks_to_apple_notes([task.to_dict() for task in tasks])
```

**Option 2: Real-time Sync (Advanced)**

Add sync calls to your task operations:

```python
# In models.py, after creating a task:
from apple_notes_integration import AppleNotesClient

def create(title, owner, ...):
    # ... existing code ...
    task_id = cursor.lastrowid

    # Sync to Apple Notes
    try:
        notes_client = AppleNotesClient()
        notes_client.create_task_note(
            Task.get_by_id(task_id).to_dict(),
            folder='Tasks'
        )
    except Exception as e:
        # Log but don't fail if sync fails
        print(f"Note sync failed: {e}")

    return task_id
```

**Option 3: Background Sync (Production)**

Use a background job (e.g., with APScheduler):

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apple_notes_integration import AppleNotesClient
from models import Task

def sync_to_notes():
    """Sync all open tasks to Apple Notes."""
    try:
        client = AppleNotesClient()
        tasks = Task.get_all_open()
        client.sync_tasks_to_notes(
            [task.to_dict() for task in tasks],
            folder='Tasks',
            clear_existing=True
        )
    except Exception as e:
        print(f"Sync error: {e}")

# Run every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(sync_to_notes, 'interval', minutes=5)
scheduler.start()
```

---

## Testing

### Test WhatsApp Integration

```bash
# Run the Flask app
python app.py

# In another terminal, send a test message
curl -X POST http://localhost:5000/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "body": "Test message"
  }'
```

### Test Apple Notes Integration

```python
# test_notes.py
from apple_notes_integration import AppleNotesClient

client = AppleNotesClient()

# Test folder access
folders = client.get_all_folders()
print(f"Found {len(folders)} folders:", folders)

# Test note creation
note = client.create_note(
    title='Test Note',
    body='This is a test',
    folder='Notes'
)
print("Created note:", note)

# Test retrieval
notes = client.get_all_notes()
print(f"Total notes: {len(notes)}")
```

---

## Troubleshooting

### WhatsApp Issues

**Problem**: Messages not being received
- Check webhook URL is correct in Twilio Console
- Verify ngrok is running (if testing locally)
- Check Twilio logs in Console for errors

**Problem**: Can't send messages
- Verify environment variables are set
- Check recipient has joined the sandbox
- Ensure phone number is in E.164 format (+1234567890)

**Problem**: 24-hour window expired
- Users must send a message to you first
- You can only respond within 24 hours
- For unrestricted messaging, upgrade to approved WhatsApp Business account

### Apple Notes Issues

**Problem**: "osascript not found"
- This integration only works on macOS
- Cannot be used on Linux/Windows servers

**Problem**: Permission denied
- macOS may require accessibility permissions
- System Preferences → Security & Privacy → Automation

**Problem**: Note not appearing
- Check folder exists in Apple Notes
- Try creating in default "Notes" folder first
- Verify note ID is correct

---

## Security Considerations

### WhatsApp
- **Never commit** Twilio credentials to version control
- Use environment variables or secure secret management
- Validate webhook requests using Twilio's signature validation
- Implement rate limiting on webhook endpoint

### Apple Notes
- Notes integration runs with your user permissions
- Only works on trusted machines (your development machine)
- Consider privacy implications of syncing sensitive task data

---

## References

### Twilio WhatsApp API
- [Twilio WhatsApp Quickstart](https://www.twilio.com/docs/whatsapp/quickstart)
- [Receive WhatsApp Messages in Python](https://www.twilio.com/en-us/blog/receive-whatsapp-messages-python-flask-twilio)
- [WhatsApp Sandbox Documentation](https://www.twilio.com/docs/whatsapp/sandbox)
- [Twilio Python Helper Library](https://www.twilio.com/docs/libraries/python)

### Apple Notes Automation
- [JavaScript for Automation Release Notes](https://developer.apple.com/library/archive/releasenotes/InterapplicationCommunication/RN-JavaScriptForAutomation/)
- [macOS Automation - Notes](http://www.macosxautomation.com/applescript/notes/index.html)
- [JXA Notes and Examples](https://www.galvanist.com/posts/2020-03-28-jxa_notes/)

---

## Next Steps

1. **Set up Twilio** and configure WhatsApp Sandbox
2. **Test webhook** by sending a message to your sandbox number
3. **Create a sync script** to periodically sync tasks to Apple Notes
4. **Deploy to production** with proper webhook URL
5. **Monitor sync reliability** and adjust strategy as needed

For questions or issues, refer to the official documentation linked above.
