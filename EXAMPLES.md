# Usage Examples

## WhatsApp Message Formats

### Creating Tasks

#### Example 1: Simple Task
```
#task
Title: Buy milk
Owner: Ofek
```

#### Example 2: Task with Due Date
```
#task
Title: Call insurance company
Owner: Wife
Due: Tomorrow 3pm
```

#### Example 3: Complete Task
```
#task
Title: Upload medical documents
Owner: Wife
Due: Thursday 20:00
Next: Ofek submits to portal
```

#### Example 4: Task with Notes
```
#task
Title: Book flight tickets
Owner: Ofek
Due: Jan 25 10am
Next: Check passport expiry
```

## URL Examples

### Quick Action URLs

Replace `{base_url}` with your actual URL (e.g., `https://yourapp.railway.app`)

#### Create Task
```
{base_url}/newTask?text=%23task%0ATitle:%20Buy%20milk%0AOwner:%20Ofek
```

#### View All Open Tasks
```
{base_url}/open
```

#### View My Tasks
```
{base_url}/mine?owner=Ofek
{base_url}/mine?owner=Wife
```

#### View Today's Tasks
```
{base_url}/today
```

#### View Specific Task
```
{base_url}/task/14
```

#### Mark Task as Done
```
{base_url}/markDone/14
```

#### Reassign Task
```
{base_url}/reassign/14?to=Wife
{base_url}/reassign/14?to=Ofek
```

#### Update Due Date
```
{base_url}/updateDue/14?date=2024-01-25 15:00
{base_url}/updateDue/14?date=Tomorrow 3pm
```

#### Update Next Step
```
{base_url}/updateNext/14?step=Call doctor for confirmation
```

## API Examples

### Using cURL

#### Create Task
```bash
curl -X POST https://yourapp.com/api/newTask \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Upload medical docs",
    "owner": "Wife",
    "due_date": "2024-01-20 20:00",
    "next_step": "Ofek submits"
  }'
```

#### Get All Tasks
```bash
curl https://yourapp.com/api/tasks
```

#### Get Tasks by Owner
```bash
curl https://yourapp.com/api/tasks?owner=Ofek
```

#### Get Specific Task
```bash
curl https://yourapp.com/api/task/14
```

### Using Python

```python
import requests

# Base URL
BASE_URL = "https://yourapp.com"

# Create a task
response = requests.post(
    f"{BASE_URL}/api/newTask",
    json={
        "title": "Buy groceries",
        "owner": "Ofek",
        "due_date": "2024-01-20 18:00",
        "next_step": "Get milk and bread"
    }
)
task = response.json()
print(f"Created task #{task['task_id']}")

# Get all open tasks
response = requests.get(f"{BASE_URL}/api/tasks?status=open")
tasks = response.json()['tasks']
print(f"Found {len(tasks)} open tasks")

# Mark task as done
task_id = 14
response = requests.post(f"{BASE_URL}/markDone/{task_id}")
print(response.json())
```

### Using JavaScript

```javascript
// Create a task
async function createTask() {
  const response = await fetch('https://yourapp.com/api/newTask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: 'Buy groceries',
      owner: 'Ofek',
      due_date: '2024-01-20 18:00',
      next_step: 'Get milk and bread'
    })
  });

  const data = await response.json();
  console.log(`Created task #${data.task_id}`);
  return data;
}

// Get all open tasks
async function getOpenTasks() {
  const response = await fetch('https://yourapp.com/api/tasks?status=open');
  const data = await response.json();
  console.log(`Found ${data.tasks.length} open tasks`);
  return data.tasks;
}

// Mark task as done
async function markDone(taskId) {
  const response = await fetch(`https://yourapp.com/markDone/${taskId}`, {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data.message);
}
```

## Real-World Workflows

### Workflow 1: Shared Grocery Shopping

**In WhatsApp:**
```
Ofek: #task
      Title: Buy groceries for Shabbat
      Owner: Wife
      Due: Friday 4pm
      Next: Check fridge and make list

[Ofek taps: Create Task → Task #15 created]

Wife: Got the list!
Ofek: [Shares link] https://yourapp.com/task/15

Wife: Done shopping!
Ofek: [Taps] https://yourapp.com/markDone/15

✅ Task completed!
```

### Workflow 2: Medical Appointment

**In WhatsApp:**
```
Wife: #task
      Title: Call dentist for checkup
      Owner: Wife
      Due: Monday 10am
      Next: Book appointment for both

[Wife taps: Create Task → Task #16 created]

Wife: Called, they have availability Tuesday 3pm
Wife: Can you go?

Ofek: Yes!
Wife: [Taps] https://yourapp.com/updateNext/16?step=Ofek confirms and adds to calendar

[Tuesday after appointment]
Ofek: Done with dentist ✓
Ofek: [Taps] https://yourapp.com/markDone/16
```

### Workflow 3: Document Submission

**In WhatsApp:**
```
Ofek: #task
      Title: Submit passport renewal docs
      Owner: Ofek
      Due: Wednesday 23:59
      Next: Scan all documents

[Create Task #17]

Ofek: Scanned everything!
Ofek: [Updates] https://yourapp.com/updateNext/17?step=Wife reviews before submission

Wife: Checked, looks good!
Wife: [Reassigns] https://yourapp.com/reassign/17?to=Ofek

Ofek: Submitted!
Ofek: [Completes] https://yourapp.com/markDone/17
```

### Workflow 4: Weekly Planning

**Every Sunday Morning:**

```
Ofek: [Taps] https://yourapp.com/mine?owner=Ofek
      → Sees all tasks for the week

Ofek: [Checks] https://yourapp.com/today
      → Sees what's due today

Ofek: [In WhatsApp] Creates new tasks for the week...

#task
Title: Prepare presentation
Owner: Ofek
Due: Tuesday 9am
Next: Draft outline

#task
Title: Pay electricity bill
Owner: Wife
Due: Friday
Next: Check amount online
```

## iPhone Shortcuts Examples

### Text Replacement Setup

Go to: Settings → General → Keyboard → Text Replacement

| Phrase (URL) | Shortcut |
|-------------|----------|
| `https://yourapp.com/open` | `ttopen` |
| `https://yourapp.com/mine?owner=Ofek` | `ttmine` |
| `https://yourapp.com/mine?owner=Wife` | `ttwife` |
| `https://yourapp.com/today` | `tttoday` |
| `https://yourapp.com/markDone/` | `ttdone` |
| `https://yourapp.com/reassign/` | `ttmove` |

### Usage in WhatsApp

**Check your tasks:**
1. Type `ttmine` in WhatsApp
2. URL expands automatically
3. Tap to open

**Mark task #14 as done:**
1. Type `ttdone14`
2. Expands to: `https://yourapp.com/markDone/14`
3. Tap to complete

**Reassign task #14:**
1. Type `ttmove14?to=Wife`
2. Expands to: `https://yourapp.com/reassign/14?to=Wife`
3. Tap to reassign

## Automation Ideas

### Daily Morning Summary

Add to cron (Linux/Mac):
```bash
# Every day at 8am, check today's tasks
0 8 * * * curl -s https://yourapp.com/api/tasks?status=open | \
  jq -r '.tasks[] | "#\(.id): \(.title) (Owner: \(.owner))"' | \
  mail -s "Today's Tasks" you@email.com
```

### Overdue Task Alerts

Create a reminder script:
```python
import requests
from datetime import datetime

response = requests.get('https://yourapp.com/api/tasks?status=open')
tasks = response.json()['tasks']

overdue = []
for task in tasks:
    if task['due_date']:
        due = datetime.fromisoformat(task['due_date'])
        if due < datetime.now():
            overdue.append(task)

if overdue:
    print("⚠️ Overdue tasks:")
    for task in overdue:
        print(f"  - #{task['id']}: {task['title']} (Owner: {task['owner']})")
```

### WhatsApp Starred Messages

Star these in WhatsApp for quick access:

```
⭐️ MY TASKS
https://yourapp.com/mine?owner=Ofek

⭐️ WIFE'S TASKS
https://yourapp.com/mine?owner=Wife

⭐️ ALL OPEN
https://yourapp.com/open

⭐️ TODAY
https://yourapp.com/today

⭐️ MARK DONE (add task # at end)
https://yourapp.com/markDone/
```

## Tips

1. **Keep URLs short**: Use a URL shortener like bit.ly for cleaner WhatsApp messages
2. **Save as contacts**: Create a fake contact named "Tasks" with URLs in notes
3. **Use Siri Shortcuts**: Create iOS shortcuts for common actions
4. **Browser bookmarks**: Save frequent URLs as mobile browser bookmarks
5. **Share liberally**: Send task URLs directly to family members

---

Need more examples? Check the README.md or open an issue!
