"""WhatsApp Task Manager Bot - Compact Edition

A simple task manager using WhatsApp + Apple Notes.
No database, no web UI, just clean task management.
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add simple-whatsapp-bot to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simple-whatsapp-bot'))

try:
    from src.WhatsAppBot import WhatsAppBot
except ImportError:
    print("ERROR: simple-whatsapp-bot not found")
    print("Make sure simple-whatsapp-bot/ directory exists")
    sys.exit(1)

import apple_notes

# Configuration
TASKS_JSON = 'tasks.json'
SYNC_INTERVAL = 300  # 5 minutes
NOTES_FOLDER = 'Tasks'


class TaskManager:
    """Manages tasks via WhatsApp and Apple Notes."""

    def __init__(self, group_name: Optional[str] = None):
        """Initialize task manager.

        Args:
            group_name: Optional WhatsApp group name to listen to
        """
        self.group_name = group_name
        self.bot = None
        self.tasks_cache = []
        self.sync_timer = None

    def start(self):
        """Start the bot and sync timer."""
        print("🤖 Starting WhatsApp Task Manager...")
        print(f"📁 Notes folder: {NOTES_FOLDER}")
        print(f"💾 Backup file: {TASKS_JSON}")

        # Load existing tasks
        self.load_tasks_from_json()

        # Initialize WhatsApp bot
        bot_config = {}
        if self.group_name:
            bot_config['groupName'] = self.group_name
            print(f"👥 Listening to group: {self.group_name}")

        self.bot = WhatsAppBot(bot_config)

        # Set up message listener
        self.bot.listen(self.handle_message)

        # Start periodic sync
        self.start_sync_timer()

        # Start bot (will show QR code if needed)
        print("\n📱 Starting WhatsApp bot...")
        self.bot.start()

        print("\n✅ Bot is ready! Send #help to WhatsApp for commands.")

    def handle_message(self, message):
        """Handle incoming WhatsApp message."""
        try:
            body = message['body'].strip()
            sender = message['from']

            print(f"\n📨 Message from {sender}: {body[:50]}...")

            # Route to appropriate handler
            if '#task' in body.lower():
                self.handle_create_task(message)
            elif any(cmd in body.lower() for cmd in ['#tasks', '#list']):
                self.handle_list_tasks(message)
            elif '#mine' in body.lower():
                self.handle_my_tasks(message)
            elif '#done' in body.lower():
                self.handle_mark_done(message)
            elif '#help' in body.lower():
                self.handle_help(message)

        except Exception as e:
            print(f"❌ Error handling message: {e}")
            try:
                message.reply(f"❌ Error: {str(e)}")
            except:
                pass

    def handle_create_task(self, message):
        """Parse and create a task from WhatsApp message."""
        task = self.parse_task(message['body'])

        if not task:
            message.reply("❌ Invalid task format. Use:\n\n#task\nTitle: <title>\nOwner: <name>")
            return

        try:
            # Create in Apple Notes
            task_with_note = apple_notes.create_task(task)

            # Add to cache
            self.tasks_cache.append(task_with_note)

            # Save to JSON
            self.save_tasks_to_json()

            # Reply with confirmation
            reply = f"✅ Task created!\n\n"
            reply += f"📝 {task['title']}\n"
            reply += f"👤 Owner: {task['owner']}\n"
            if task.get('due'):
                reply += f"📅 Due: {task['due']}\n"
            reply += f"\n🆔 ID: {task['id']}\n\n"
            reply += f"Use '#done {task['id']}' to mark complete"

            message.reply(reply)

            print(f"✅ Task created: {task['id']}")

        except Exception as e:
            print(f"❌ Error creating task: {e}")
            message.reply(f"❌ Error creating task: {str(e)}\nTask saved to backup only.")

            # Save to JSON even if Notes fails
            self.tasks_cache.append(task)
            self.save_tasks_to_json()

    def handle_list_tasks(self, message):
        """List all open tasks."""
        try:
            # Try to get from Notes first
            try:
                tasks = apple_notes.get_all_tasks()
                self.tasks_cache = tasks
                self.save_tasks_to_json()
            except Exception as e:
                print(f"⚠️ Notes unavailable, using cache: {e}")
                tasks = self.tasks_cache

            # Filter open tasks
            open_tasks = [t for t in tasks if t.get('status') == 'open']

            if not open_tasks:
                message.reply("📭 No open tasks!")
                return

            # Sort by priority (high first) and due date
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            open_tasks.sort(key=lambda t: (
                priority_order.get(t.get('priority', 'medium'), 1),
                t.get('due', 'ZZZ')  # Tasks without due date go last
            ))

            # Format list
            reply = "📋 *Open Tasks*\n\n"

            for i, task in enumerate(open_tasks[:10], 1):  # Limit to 10
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(
                    task.get('priority', 'medium'), '🟡'
                )

                reply += f"{i}. {priority_emoji} {task['title']}\n"
                reply += f"   👤 {task['owner']}"
                if task.get('due'):
                    reply += f" | 📅 {task['due']}"
                reply += f"\n   🆔 {task['id']}\n\n"

            if len(open_tasks) > 10:
                reply += f"_...and {len(open_tasks) - 10} more tasks_"

            message.reply(reply)

        except Exception as e:
            print(f"❌ Error listing tasks: {e}")
            message.reply(f"❌ Error: {str(e)}")

    def handle_my_tasks(self, message):
        """List tasks for specific owner (extracted from message)."""
        try:
            # Try to extract owner from message
            body = message['body'].lower()
            words = body.split()

            # Look for owner name after #mine
            owner = None
            if '#mine' in words:
                idx = words.index('#mine')
                if idx + 1 < len(words):
                    owner = words[idx + 1].capitalize()

            if not owner:
                message.reply("❓ Specify owner: #mine <name>")
                return

            # Get all tasks
            try:
                tasks = apple_notes.get_all_tasks()
                self.tasks_cache = tasks
            except Exception:
                tasks = self.tasks_cache

            # Filter by owner and status
            my_tasks = [t for t in tasks
                       if t.get('status') == 'open' and t.get('owner', '').lower() == owner.lower()]

            if not my_tasks:
                message.reply(f"📭 No open tasks for {owner}")
                return

            # Format list
            reply = f"📋 *Tasks for {owner}*\n\n"

            for i, task in enumerate(my_tasks[:10], 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(
                    task.get('priority', 'medium'), '🟡'
                )

                reply += f"{i}. {priority_emoji} {task['title']}\n"
                if task.get('due'):
                    reply += f"   📅 {task['due']}\n"
                if task.get('next'):
                    reply += f"   ➡️ {task['next']}\n"
                reply += f"   🆔 {task['id']}\n\n"

            message.reply(reply)

        except Exception as e:
            print(f"❌ Error: {e}")
            message.reply(f"❌ Error: {str(e)}")

    def handle_mark_done(self, message):
        """Mark a task as done."""
        try:
            # Extract task ID
            body = message['body']
            words = body.split()

            task_id = None
            for word in words:
                if word.startswith('task_'):
                    task_id = word
                    break

            if not task_id:
                message.reply("❓ Specify task ID: #done task_xxx")
                return

            # Find task in cache
            task = next((t for t in self.tasks_cache if t['id'] == task_id), None)

            if not task:
                message.reply(f"❌ Task {task_id} not found")
                return

            # Mark done in Notes
            success = False
            try:
                success = apple_notes.mark_done(task_id)
            except Exception as e:
                print(f"⚠️ Could not update Notes: {e}")

            # Update cache
            task['status'] = 'done'
            task['completed_at'] = datetime.now().isoformat()
            self.save_tasks_to_json()

            # Reply
            reply = f"✅ Task completed!\n\n"
            reply += f"📝 {task['title']}\n"
            reply += f"👤 {task['owner']}"

            if not success:
                reply += "\n\n⚠️ Updated backup only (Notes unavailable)"

            message.reply(reply)

            print(f"✅ Task marked done: {task_id}")

        except Exception as e:
            print(f"❌ Error: {e}")
            message.reply(f"❌ Error: {str(e)}")

    def handle_help(self, message):
        """Send help message with available commands."""
        help_text = """📝 *Task Manager Commands*

*Create Task:*
#task
Title: <task title>
Owner: <person name>
Due: <date/time> (optional)
Next: <next action> (optional)
Priority: high/medium/low (optional)

*List Tasks:*
#tasks - Show all open tasks
#list - Same as #tasks
#mine <name> - Show tasks for specific owner

*Complete Task:*
#done task_xxx - Mark task as done

*Help:*
#help - Show this message

---
Tasks are stored in Apple Notes "Tasks" folder.
Backup: tasks.json"""

        message.reply(help_text)

    def parse_task(self, text: str) -> Optional[Dict]:
        """Parse WhatsApp message into task dict.

        Expected format:
            #task
            Title: Buy groceries
            Owner: Ofek
            Due: Tomorrow 6pm
            Next: Make list
            Priority: high
        """
        if '#task' not in text.lower():
            return None

        task = {
            'id': f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }

        # Parse line by line
        lines = text.strip().split('\n')
        for line in lines:
            if ':' not in line or line.strip().startswith('#'):
                continue

            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            # Map keys to task fields
            field_map = {
                'title': 'title',
                'owner': 'owner',
                'due': 'due',
                'next': 'next',
                'priority': 'priority',
                'notes': 'notes'
            }

            if key in field_map:
                task[field_map[key]] = value

        # Validate required fields
        if 'title' not in task or 'owner' not in task:
            return None

        # Set defaults
        task.setdefault('priority', 'medium')

        return task

    def load_tasks_from_json(self):
        """Load tasks from JSON backup."""
        try:
            if os.path.exists(TASKS_JSON):
                with open(TASKS_JSON, 'r') as f:
                    self.tasks_cache = json.load(f)
                print(f"📂 Loaded {len(self.tasks_cache)} tasks from backup")
            else:
                self.tasks_cache = []
                print("📂 No backup file found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading backup: {e}")
            self.tasks_cache = []

    def save_tasks_to_json(self):
        """Save tasks to JSON backup."""
        try:
            with open(TASKS_JSON, 'w') as f:
                json.dump(self.tasks_cache, f, indent=2)
            print(f"💾 Saved {len(self.tasks_cache)} tasks to backup")
        except Exception as e:
            print(f"⚠️ Error saving backup: {e}")

    def sync_notes_to_json(self):
        """Sync tasks from Apple Notes to JSON (periodic background task)."""
        try:
            print("\n🔄 Syncing from Apple Notes...")
            tasks = apple_notes.get_all_tasks()
            self.tasks_cache = tasks
            self.save_tasks_to_json()
            print(f"✅ Sync complete: {len(tasks)} tasks")
        except Exception as e:
            print(f"⚠️ Sync failed: {e}")

    def start_sync_timer(self):
        """Start periodic sync timer."""
        def sync_loop():
            while True:
                time.sleep(SYNC_INTERVAL)
                self.sync_notes_to_json()

        self.sync_timer = threading.Thread(target=sync_loop, daemon=True)
        self.sync_timer.start()
        print(f"⏰ Auto-sync enabled (every {SYNC_INTERVAL//60} minutes)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Task Manager Bot')
    parser.add_argument('--group', help='WhatsApp group name to listen to', default=None)
    args = parser.parse_args()

    # Create and start manager
    manager = TaskManager(group_name=args.group)

    try:
        manager.start()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        if manager.bot:
            manager.bot.stop()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
