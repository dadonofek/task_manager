# Quick Start Guide

## 5-Minute Setup

### 1. Install and Run

```bash
pip install -r requirements.txt
python app.py
```

Server runs at: `http://localhost:5000`

### 2. Create Your First Task

**Option A: Via Browser**
1. Open: `http://localhost:5000/open`
2. Use the web interface

**Option B: Via Quick Link (WhatsApp-style)**
1. Copy this URL:
```
http://localhost:5000/newTask?text=%23task%0ATitle:%20Buy%20groceries%0AOwner:%20Ofek%0ADue:%20Today%206pm%0ANext:%20Pick%20up%20milk
```
2. Paste in browser
3. Task created!

**Option C: Via API**
```bash
curl -X POST http://localhost:5000/api/newTask \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "owner": "Ofek",
    "due_date": "2024-01-20 18:00",
    "next_step": "Pick up milk"
  }'
```

### 3. View Your Tasks

- All open: `http://localhost:5000/open`
- My tasks: `http://localhost:5000/mine?owner=Ofek`
- Today: `http://localhost:5000/today`

### 4. Quick Actions

**Mark task #1 as done:**
```
http://localhost:5000/markDone/1
```

**Reassign task #1 to Wife:**
```
http://localhost:5000/reassign/1?to=Wife
```

**Update due date:**
```
http://localhost:5000/updateDue/1?date=2024-01-21 15:00
```

## iPhone Keyboard Shortcuts

### Setup

1. Settings → General → Keyboard → Text Replacement
2. Add shortcuts:

| Phrase | Shortcut |
|--------|----------|
| `https://yourapp.com/open` | `ttopen` |
| `https://yourapp.com/mine?owner=Ofek` | `ttmine` |
| `https://yourapp.com/markDone/` | `ttdone` |
| `https://yourapp.com/reassign/` | `ttrsgn` |

### Usage in WhatsApp

1. Type `ttmine` → auto-expands to your tasks URL
2. Tap the link → opens in browser
3. Done!

## WhatsApp Workflow

### Creating a Task

**In WhatsApp:**
```
#task
Title: Call dentist
Owner: Wife
Due: Tomorrow 2pm
Next: Book appointment
```

**Then:**
1. Long-press and copy the message
2. Type `ttnew` (your keyboard shortcut)
3. Paste the task text
4. Open the generated URL
5. Task created + you get quick action links!

### Marking Complete

**In WhatsApp:**
```
You: Done with the dentist call!

[Type: ttdone14]  (expands to: https://yourapp.com/markDone/14)
[Tap the link]

✅ Task #14 marked as done!
```

### Checking Tasks

**In WhatsApp:**
```
You: What do I need to do today?

[Type: tttoday]  (expands to: https://yourapp.com/today)
[Tap the link]

Browser opens with today's tasks!
```

## Production Deployment

### Railway (Easiest, Free)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Get URL
railway domain
```

Your app is live at: `https://yourapp.railway.app`

### Fly.io (Free, More Control)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch

# Your app: https://yourapp.fly.dev
```

### Update Shortcuts

After deployment, update your iPhone shortcuts to use your production URL:
- `https://yourapp.railway.app/open` instead of `localhost:5000/open`

## Tips & Tricks

### 1. Star Messages in WhatsApp

Save quick action URLs as starred messages:
```
⭐️ Mark Done #14: https://yourapp.com/markDone/14
⭐️ My Tasks: https://yourapp.com/mine?owner=Ofek
⭐️ Today: https://yourapp.com/today
```

Access via: WhatsApp menu → Starred messages

### 2. Share URLs Directly

```
You: Can you handle this task?
Wife: Sure!
You: https://yourapp.com/task/14
     [Quick actions are in the page]
```

### 3. Morning Routine

Every morning:
1. Tap `tttoday` in WhatsApp
2. See your tasks for the day
3. Done!

### 4. End-of-Day Review

Every evening:
1. Tap `ttmine` to see your open tasks
2. Mark completed ones as done
3. Plan tomorrow

## Troubleshooting

**Port already in use:**
```bash
python app.py --port 5001
```

**Database locked:**
```bash
rm tasks.db
python -c "from database import init_db; init_db()"
```

**Can't connect from phone:**
- Use your computer's IP address: `http://192.168.1.x:5000`
- Or deploy to Railway/Fly.io

## Next Steps

1. ✅ Create 3-5 test tasks
2. ✅ Set up iPhone keyboard shortcuts
3. ✅ Practice the WhatsApp workflow
4. ✅ Deploy to Railway/Fly.io
5. ✅ Update shortcuts with production URL
6. ✅ Enjoy stress-free task management!

---

**Need help?** Check the main README.md or open an issue!
