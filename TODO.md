# TODO: Future Enhancements

Last updated: 2025-11-26
Current version: JSON-only, 124 lines

---

## 🎯 Quick Wins (Easy to Test & Implement)

These are simple UI improvements that can be tested via WhatsApp messages and implemented in 10-30 minutes.

### Command Improvements
- [ ] **#delete command** - Delete a task: `#delete task_xxx`
  - Test: Create task, delete it, verify it's gone from JSON
  - Implementation: Find task by ID, remove from array, save JSON

- [ ] **#edit command** - Edit task fields: `#edit task_xxx title: New Title`
  - Test: Create task, edit title/owner/due, verify changes in JSON
  - Implementation: Parse field updates, find task, update, save

- [ ] **#search command** - Search tasks by keyword: `#search groceries`
  - Test: Create tasks with different titles, search, verify results
  - Implementation: Filter tasks array by keyword in title/owner/next

- [ ] **#completed command** - Show recently completed tasks: `#completed`
  - Test: Complete some tasks, run command, verify output
  - Implementation: Filter by status='done', sort by completed_at, format list

- [ ] **#stats command** - Show task statistics
  - Test: Create/complete tasks, verify stats are accurate
  - Implementation: Count open/done, group by priority, format output
  - Example output: `📊 *Stats*\n5 open, 12 completed\n🔴 2 high, 🟡 3 medium`

### Better Formatting
- [ ] **Show "next" in task list** - Display next action in `#tasks` output
  - Test: Create task with "Next" field, verify it shows in list
  - Implementation: Add `next` field to formatList() output

- [ ] **Show task age** - Display "Created 2 days ago"
  - Test: Create old task (manually edit created_at), verify age shown
  - Implementation: Calculate time diff, format human-readable

- [ ] **Better priority colors** - Use more emoji: 🔥⚡🟢
  - Test: Create tasks with different priorities, verify emoji
  - Implementation: Update emoji map in formatList()

- [ ] **Task numbering in replies** - Show "Task #5 created"
  - Test: Create task, verify number in response
  - Implementation: Count total tasks, show position

### Smart Defaults
- [ ] **Remember last owner** - Auto-fill owner from previous task
  - Test: Create task as Owner A, create another without owner, verify auto-fill
  - Implementation: Cache last owner in memory, use if not specified

- [ ] **Default priority based on keywords** - "urgent" → high priority
  - Test: Create task with "urgent" in title, verify priority=high
  - Implementation: Keyword matching in parseTask()

### Better Error Messages
- [ ] **Show available owners** - When using `#mine`, suggest existing owners
  - Test: Run `#mine` with wrong name, verify suggestion
  - Implementation: Collect unique owners from tasks, suggest in error

- [ ] **Suggest corrections** - "Did you mean #tasks?" when typo
  - Test: Send `#task` (typo), verify helpful response
  - Implementation: Fuzzy matching on commands

---

## 🚀 Medium Effort Features (1-2 hours)

### Filtering & Views
- [ ] **#high / #medium / #low** - Filter by priority
  - Test: Create mixed priorities, filter, verify results
  - Implementation: Filter tasks by priority, reuse formatList()

- [ ] **#overdue** - Show tasks past due date
  - Test: Create tasks with past dates, verify overdue shown
  - Implementation: Parse due dates, compare to today, filter

- [ ] **#today / #week** - Filter by due date range
  - Test: Create tasks with different due dates, verify filtering
  - Implementation: Date parsing and comparison

### Bulk Operations
- [ ] **#complete-all** - Mark all of my tasks as done
  - Test: Create multiple tasks, complete all at once
  - Implementation: Filter by owner, update all to done, save

- [ ] **#delete-completed** - Archive old completed tasks
  - Test: Complete tasks, archive them, verify they're moved
  - Implementation: Filter completed, save to archive.json, remove from tasks

### Better Task Creation
- [ ] **Quick create** - Shorthand: `#t Buy milk @Ofek !high`
  - Test: Use shorthand syntax, verify task created correctly
  - Implementation: Alternative parser for compact format

- [ ] **Task from message** - Auto-create from forwarded messages
  - Test: Forward message, verify task created from content
  - Implementation: Detect forwarded messages, extract text

### Export & Backup
- [ ] **#export** - Get all tasks as formatted text
  - Test: Run export, verify readable format returned
  - Implementation: Generate markdown/CSV, send as message

- [ ] **Auto-backup** - Save daily backup to tasks_backup_YYYYMMDD.json
  - Test: Wait 24h, verify backup created
  - Implementation: Cron-like daily check, copy JSON with date stamp

---

## 💡 Advanced Features (2-4 hours)

### Notifications & Reminders
- [ ] **Daily summary** - Send morning summary to group/users
  - Test: Set time, verify summary sent daily
  - Implementation: setInterval() to check time, send formatList()

- [ ] **Due date reminders** - Alert when task due today/tomorrow
  - Test: Create task due tomorrow, verify reminder sent
  - Implementation: Daily check for upcoming due dates, send alerts

- [ ] **@mention notifications** - Notify owner when assigned task
  - Test: Create task for someone, verify they get notification
  - Implementation: Send direct message to owner when task created

### Categories & Tags
- [ ] **Category field** - Add `Category: Work/Personal/Shopping`
  - Test: Create tasks with categories, filter by category
  - Implementation: Add category to parseTask(), filter commands

- [ ] **#tags** - Support hashtags: `#task Buy milk #shopping #urgent`
  - Test: Create task with tags, search by tag
  - Implementation: Extract hashtags, store in array, search

### Task Dependencies
- [ ] **Blocked by** - Mark task as blocked: `#block task_xxx by task_yyy`
  - Test: Block a task, verify it shows in list with indicator
  - Implementation: Add blocked_by field, show 🔒 in list

- [ ] **Subtasks** - Break down tasks: `#subtask task_xxx: Step 1`
  - Test: Add subtasks, verify they show under parent
  - Implementation: Add parent_id field, nested display

---

## 🔧 Code Quality & Testing

### Testing
- [ ] **Add unit tests** - Test parseTask(), formatList(), loadTasks()
  - Use Jest or Node's built-in test runner
  - Test edge cases (empty JSON, malformed tasks, etc.)

- [ ] **Integration tests** - Test full command flows
  - Mock WhatsApp message objects
  - Verify JSON changes after commands

### Refactoring
- [ ] **Extract commands to handlers** - One function per command
  - Cleaner code organization
  - Easier to test individually

- [ ] **Configuration file** - Move settings to config.json
  - GROUP_NAME, Chrome path, JSON file path
  - Environment-specific configs

### Error Handling
- [ ] **Better error messages** - User-friendly error descriptions
- [ ] **Error logging** - Log errors to file with timestamps
- [ ] **Graceful degradation** - Handle missing fields gracefully

---

## 🌐 Platform & Deployment

### Cross-Platform
- [ ] **Windows support** - Test Chrome path on Windows
- [ ] **Linux support** - Test on Ubuntu/Debian
- [ ] **Docker container** - Package for easy deployment

### Production
- [ ] **Process manager** - Use PM2 for auto-restart
- [ ] **Systemd service** - Auto-start on boot (Linux)
- [ ] **LaunchAgent** - Auto-start on macOS
- [ ] **Health checks** - Ping endpoint to verify bot is alive

---

## 📊 Analytics & Insights

### Statistics
- [ ] **Completion rate** - % of tasks completed
- [ ] **Average completion time** - Time from creation to done
- [ ] **Top performers** - Who completes most tasks
- [ ] **Trend charts** - Send chart images with weekly trends

### Reporting
- [ ] **Weekly report** - Automated weekly summary
- [ ] **Personal stats** - `#mystats` for individual metrics
- [ ] **Team leaderboard** - Gamification element

---

## 🎨 UI Polish

### Message Formatting
- [ ] **Better emoji** - More visual indicators (✓ ✗ ⏰ 🏃 🎯)
- [ ] **Rich text** - Use WhatsApp formatting (*bold*, _italic_)
- [ ] **Interactive buttons** - WhatsApp button integration
- [ ] **Progress bars** - ASCII progress: `[=====>    ] 50%`

### Customization
- [ ] **Custom emoji per user** - Let users choose priority emoji
- [ ] **Themes** - Different formatting styles
- [ ] **Language support** - i18n for multiple languages

---

## 🔒 Security & Privacy

### Access Control
- [ ] **Pin protection** - Require PIN for sensitive commands
- [ ] **Owner-only delete** - Only task owner can delete/complete
- [ ] **Admin commands** - Special commands for group admin
- [ ] **Rate limiting** - Prevent spam/abuse

### Data Protection
- [ ] **Encrypt tasks.json** - AES encryption for sensitive tasks
- [ ] **Data export** - GDPR compliance - export user's tasks
- [ ] **Data deletion** - Delete all user data on request
- [ ] **Audit log** - Track who did what

---

## 🚀 Integrations

### External Services
- [ ] **Google Calendar sync** - Create calendar events for due dates
- [ ] **Email notifications** - Send email for important updates
- [ ] **Slack webhook** - Mirror tasks to Slack channel
- [ ] **GitHub issues** - Create issues from tasks

### APIs
- [ ] **REST API** - HTTP API for external access
- [ ] **Webhooks** - Trigger external services on events
- [ ] **Import/Export** - Support CSV, JSON, Markdown formats

---

## 📝 Known Issues

### Current Limitations
- ✅ ~~macOS only~~ - Now cross-platform with JSON!
- [ ] **WhatsApp Web dependency** - Requires browser connection
- [ ] **Limited to 10 tasks per list** - WhatsApp message length limit
- [ ] **No real-time collaboration** - JSON conflicts with concurrent edits
- [ ] **No image/file attachments** - Text-only tasks

### Bug Fixes Needed
- [ ] **Unicode handling** - Test with emoji-heavy messages
- [ ] **Long task titles** - Truncate or split long titles
- [ ] **Special characters** - Handle quotes, apostrophes in fields
- [ ] **Date parsing** - Better handling of ambiguous dates
- [ ] **Concurrent writes** - File locking for simultaneous edits

---

## 🎓 Getting Started for Contributors

### Pick Your First Feature
1. Choose a "Quick Win" from the top section
2. Write a test case first (what should happen?)
3. Implement in bot.js (usually 10-30 lines)
4. Test via WhatsApp
5. Commit and create PR

### Testing Checklist
- [ ] Create test tasks with different fields
- [ ] Test edge cases (empty, missing fields, special chars)
- [ ] Verify tasks.json is valid after operation
- [ ] Test error messages for invalid input
- [ ] Check that existing functionality still works

---

## 💡 Ideas for Future Exploration

- Voice message support (transcription)
- Natural language parsing ("Remind me to buy milk tomorrow")
- AI-powered task suggestions
- Habit tracking alongside tasks
- Time tracking and pomodoro timer
- Location-based reminders
- Smart home integration
- Fitness/health goal tracking

---

**Priority Legend:**
- 🎯 Quick wins - Start here! (10-30 mins)
- 🚀 Medium effort - Good second features (1-2 hours)
- 💡 Advanced - More complex (2-4 hours+)

**Pick what interests you most and have fun building!** 🚀
