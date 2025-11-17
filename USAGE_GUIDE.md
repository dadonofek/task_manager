# Usage Guide - WhatsApp Task Manager

## Quick Start

### 1. Start the Application
```bash
./start.sh
```
- Starts Flask on port 5001
- Starts WhatsApp bot
- Scan QR code on first run

### 2. Create Your First Task

**In WhatsApp Group:**
```
#task
Title: Buy groceries
Owner: Ofek
Priority: high
Category: shopping
Due: Tomorrow 6pm
Next: Make shopping list
```

**Bot Replies:**
```
✅ Task #1 Created!

📋 Buy groceries
👤 Ofek
🔴 Priority: high
🏷️ Category: shopping
⏰ Due: Tomorrow 6pm
➡️ Next: Make shopping list

Quick Actions:
✅ Mark Done: http://localhost:5001/markDone/1
👥 Reassign to Ofek: http://localhost:5001/reassign/1?to=Ofek
👥 Reassign to Shachar: http://localhost:5001/reassign/1?to=Shachar
🔗 View: http://localhost:5001/task/1
```

## Priority Levels

| Priority | Emoji | When to Use | Example |
|----------|-------|-------------|---------|
| **High** 🔴 | `Priority: high` | Urgent, time-sensitive | Fix production bug, Important meeting |
| **Medium** 🟡 | `Priority: medium` | Normal tasks (default) | Weekly errands, Regular work |
| **Low** 🟢 | `Priority: low` | Can wait, nice-to-have | Clean garage, Read article |

**Note**: Tasks are automatically sorted by priority (high first), then by due date.

## Categories

Use categories to organize tasks by type:

| Category | Use For | Examples |
|----------|---------|----------|
| **work** | Professional tasks | Meetings, reports, emails |
| **home** | Household tasks | Repairs, cleaning, maintenance |
| **shopping** | Purchases | Groceries, clothes, supplies |
| **personal** | Personal development | Exercise, reading, hobbies |
| **finance** | Money matters | Bills, taxes, budgeting |
| **health** | Medical/wellness | Doctor appointments, prescriptions |

**Custom Categories**: Create any category you need!

## WhatsApp Commands

### Create Task
```
#task
Title: [Required]
Owner: [Required - Ofek or Shachar]
Priority: [Optional - high|medium|low]
Category: [Optional - any text]
Due: [Optional - flexible date format]
Next: [Optional - next action]
```

### List Tasks
- `#tasks` or `#list` - All open tasks
- `#my` or `#mine` - Your tasks
- `#my Shachar` - Shachar's tasks

### Get Help
- `#help` or `#?` - Show all commands

### Quick Actions
Tap links in bot messages to:
- ✅ Mark task done
- 👥 Reassign to someone else
- 🔗 View full task details

## Web Interface

### Browse Tasks
- **All Open**: http://localhost:5001/open
- **Ofek's Tasks**: http://localhost:5001/mine?owner=Ofek
- **Shachar's Tasks**: http://localhost:5001/mine?owner=Shachar
- **Due Today**: http://localhost:5001/today
- **Specific Task**: http://localhost:5001/task/1

### Features
- Tasks sorted by priority automatically
- Priority indicators (🔴🟡🟢)
- Category labels (🏷️)
- Due date warnings
- Quick action buttons

## API Usage

### Create Task
```bash
curl -X POST http://localhost:5001/api/newTask \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important meeting",
    "owner": "Ofek",
    "priority": "high",
    "category": "work",
    "due_date": "2025-11-18 14:00"
  }'
```

### Get All Tasks
```bash
curl http://localhost:5001/api/tasks
```

### Filter by Priority
```bash
curl http://localhost:5001/api/tasks?priority=high
```

### Filter by Category
```bash
curl http://localhost:5001/api/tasks?category=shopping
```

### Combined Filters
```bash
curl "http://localhost:5001/api/tasks?owner=Ofek&priority=high&category=work"
```

### Get Single Task
```bash
curl http://localhost:5001/api/task/1
```

## Common Workflows

### Morning Routine
1. Open WhatsApp group
2. Send: `#tasks`
3. Review high priority items (🔴)
4. Tap quick action links to update

### Create Urgent Task
```
#task
Title: Critical bug in production
Owner: Ofek
Priority: high
Category: work
Due: Today 5pm
Next: Check error logs
```

### Weekly Planning
1. Browse: http://localhost:5001/open
2. Review by priority
3. Reassign tasks if needed
4. Update due dates

### Shopping List
```
#task
Title: Weekly grocery run
Owner: Shachar
Priority: medium
Category: shopping
Due: Saturday morning
Next: Check pantry inventory
```

### Delegate Task
1. Find task in WhatsApp or web
2. Tap "Reassign to..." link
3. Task automatically reassigned

## Priority Tips

### When to Use HIGH 🔴
- Deadlines today/tomorrow
- Blocking other work
- Client requests
- Time-sensitive errands

### When to Use MEDIUM 🟡
- Regular weekly tasks
- Standard errands
- Routine work
- Flexible deadlines

### When to Use LOW 🟢
- Nice-to-have tasks
- Long-term projects
- Non-urgent improvements
- Someday/maybe items

## Category Organization Ideas

### Work
- `urgent-work`, `meeting`, `email`, `report`

### Home
- `cleaning`, `repairs`, `maintenance`, `garden`

### Shopping
- `groceries`, `clothes`, `electronics`, `gifts`

### Personal
- `health`, `fitness`, `learning`, `hobbies`

### Family
- `kids`, `school`, `activities`, `events`

## Troubleshooting

### Bot not responding
1. Check Flask is running: http://localhost:5001/health
2. Check group name matches config
3. Restart bot: `./start.sh`

### Tasks not sorted by priority
1. Run migration: `python migrate_db.py`
2. Existing tasks get default `medium` priority
3. New tasks will sort correctly

### Can't create task
- Check required fields: Title and Owner
- Verify priority is: high, medium, or low (case-insensitive)
- Use correct format with colons

## Advanced Usage

### Python API
```python
from models import Task

# Create high priority task
task_id = Task.create(
    title="Fix bug",
    owner="Ofek",
    priority="high",
    category="work"
)

# Update priority
Task.update_priority(task_id, "low")

# Filter tasks
high_tasks = Task.get_by_priority("high")
work_tasks = Task.get_by_category("work")

# Combined filter
urgent_work = Task.get_by_filters(
    owner="Ofek",
    priority="high",
    category="work"
)
```

### Database Queries
```bash
sqlite3 tasks.db

# High priority tasks
SELECT * FROM tasks WHERE priority='high' AND status='open';

# Tasks by category
SELECT category, COUNT(*) FROM tasks
WHERE status='open' GROUP BY category;

# Priority distribution
SELECT priority, COUNT(*) FROM tasks
WHERE status='open' GROUP BY priority;
```

## Best Practices

1. **Set Priority on Creation** - Easier than updating later
2. **Review High Priority Daily** - Keep urgent list manageable
3. **Use Categories Consistently** - Easier filtering and reporting
4. **Update Priority** - Escalate/de-escalate as needed
5. **Complete Tasks** - Mark done to keep list clean
6. **Regular Review** - Weekly check of all open tasks

## Tips for Families

- **Morning Check**: Review high priority together
- **Evening Sync**: Mark completed tasks done
- **Weekly Planning**: Sunday review of upcoming tasks
- **Fair Distribution**: Balance tasks between family members
- **Priority Agreement**: Discuss what counts as "high priority"
- **Category Standards**: Agree on category names to use

## Keyboard Shortcuts (Future)

Save these as iOS keyboard shortcuts for quick task creation:
- `ttwork` → Full work task template
- `ttshop` → Shopping task template
- `tthome` → Home task template
- `tturgent` → High priority task template

---

**Need Help?** Send `#help` in WhatsApp or check FEATURES.md for technical details.
