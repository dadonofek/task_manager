"""Apple Notes integration via JXA (JavaScript for Automation).

Simple wrapper for creating, reading, and updating tasks in Apple Notes.
macOS only - requires Apple Notes app.
"""

import subprocess
import json
import re
from datetime import datetime
from typing import List, Dict, Optional


class AppleNotesClient:
    """Client for managing tasks in Apple Notes via JXA."""

    def __init__(self, folder='Tasks'):
        """Initialize client with specified Notes folder."""
        self.folder = folder
        self._check_macos()

    @staticmethod
    def _check_macos():
        """Verify running on macOS."""
        import platform
        if platform.system() != 'Darwin':
            raise RuntimeError("Apple Notes only works on macOS")

    def _run_jxa(self, script: str) -> str:
        """Execute JXA script and return output."""
        try:
            result = subprocess.run(
                ['osascript', '-l', 'JavaScript', '-e', script],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"JXA failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("osascript not found - macOS required")
        except subprocess.TimeoutExpired:
            raise RuntimeError("JXA script timeout")

    def create_task(self, task: Dict) -> Dict:
        """Create a formatted task note in Apple Notes.

        Args:
            task: Dict with keys: id, title, owner, due, next, priority, status, created_at

        Returns:
            Task dict with note_id added
        """
        # Format task for Notes with emoji
        priority = task.get('priority', 'medium').lower()
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '🟡')

        title = f"{priority_emoji} [{priority.upper()}] {task['title']}"

        body_lines = [
            f"<h2>{task['title']}</h2>",
            f"<p>👤 <strong>Owner:</strong> {task['owner']}</p>",
        ]

        if task.get('due'):
            body_lines.append(f"<p>📅 <strong>Due:</strong> {task['due']}</p>")

        if task.get('next'):
            body_lines.append(f"<p>➡️ <strong>Next:</strong> {task['next']}</p>")

        status_emoji = '⚪' if task.get('status') == 'open' else '✅'
        status_text = task.get('status', 'open').capitalize()

        body_lines.extend([
            "<br>",
            f"<p><strong>Status:</strong> {status_emoji} {status_text}</p>",
            f"<p><em>Created: {datetime.fromisoformat(task['created_at']).strftime('%Y-%m-%d %H:%M')}</em></p>",
            f"<p><em>ID: {task['id']}</em></p>",
        ])

        body = "<html><body>" + "".join(body_lines) + "</body></html>"

        # Escape for JXA
        title_esc = title.replace('\\', '\\\\').replace('"', '\\"')
        body_esc = body.replace('\\', '\\\\').replace('"', '\\"')
        folder_esc = self.folder.replace('\\', '\\\\').replace('"', '\\"')

        script = f"""
        const app = Application('Notes');
        const defaultAccount = app.defaultAccount();

        let targetFolder;
        try {{
            targetFolder = defaultAccount.folders.byName("{folder_esc}");
        }} catch (e) {{
            const newFolder = app.Folder({{name: "{folder_esc}"}});
            defaultAccount.folders.push(newFolder);
            targetFolder = newFolder;
        }}

        const note = app.Note({{
            name: "{title_esc}",
            body: "{body_esc}"
        }});

        targetFolder.notes.push(note);

        JSON.stringify({{
            note_id: note.id(),
            name: note.name()
        }});
        """

        result = self._run_jxa(script)
        note_data = json.loads(result)
        task['note_id'] = note_data['note_id']
        return task

    def get_all_tasks(self) -> List[Dict]:
        """Get all tasks from Notes folder.

        Returns:
            List of task dicts parsed from notes
        """
        folder_esc = self.folder.replace('\\', '\\\\').replace('"', '\\"')

        script = f"""
        const app = Application('Notes');
        const defaultAccount = app.defaultAccount();

        let notes;
        try {{
            const folder = defaultAccount.folders.byName("{folder_esc}");
            notes = folder.notes();
        }} catch (e) {{
            notes = [];
        }}

        const result = [];
        for (let i = 0; i < notes.length; i++) {{
            const note = notes[i];
            result.push({{
                note_id: note.id(),
                name: note.name(),
                body: note.body(),
                modified: note.modificationDate().toISOString()
            }});
        }}

        JSON.stringify(result);
        """

        result = self._run_jxa(script)
        notes = json.loads(result) if result else []

        # Parse notes into task dicts
        tasks = []
        for note in notes:
            task = self._parse_note_to_task(note)
            if task:
                tasks.append(task)

        return tasks

    def _parse_note_to_task(self, note: Dict) -> Optional[Dict]:
        """Parse a note dict into a task dict."""
        body = note['body']

        # Extract ID from body
        id_match = re.search(r'ID:\s*(\S+)', body)
        if not id_match:
            return None

        task_id = id_match.group(1)

        # Extract fields
        owner_match = re.search(r'Owner:\s*([^\n<]+)', body)
        due_match = re.search(r'Due:\s*([^\n<]+)', body)
        next_match = re.search(r'Next:\s*([^\n<]+)', body)
        status_match = re.search(r'Status:.*?(Open|Done)', body, re.IGNORECASE)
        created_match = re.search(r'Created:\s*([^\n<]+)', body)

        # Extract title and priority from note name
        title = note['name']
        priority = 'medium'

        if '[HIGH]' in title:
            priority = 'high'
        elif '[LOW]' in title:
            priority = 'low'

        # Remove emoji and priority from title
        title = re.sub(r'^[🔴🟡🟢]\s*\[[A-Z]+\]\s*', '', title)

        task = {
            'id': task_id,
            'title': title,
            'owner': owner_match.group(1).strip() if owner_match else 'Unknown',
            'due': due_match.group(1).strip() if due_match else None,
            'next': next_match.group(1).strip() if next_match else None,
            'priority': priority,
            'status': status_match.group(1).lower() if status_match else 'open',
            'created_at': created_match.group(1) if created_match else note.get('modified', ''),
            'completed_at': None,
            'note_id': note['note_id']
        }

        return task

    def mark_done(self, task_id: str) -> bool:
        """Mark a task as done by updating its note.

        Args:
            task_id: Task ID to mark done

        Returns:
            True if successful
        """
        # Get all tasks and find the one to update
        tasks = self.get_all_tasks()
        task = next((t for t in tasks if t['id'] == task_id), None)

        if not task:
            return False

        # Update task status
        task['status'] = 'done'
        task['completed_at'] = datetime.now().isoformat()

        # Recreate note body with updated status
        priority = task.get('priority', 'medium').lower()
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(priority, '🟡')

        body_lines = [
            f"<h2>{task['title']}</h2>",
            f"<p>👤 <strong>Owner:</strong> {task['owner']}</p>",
        ]

        if task.get('due'):
            body_lines.append(f"<p>📅 <strong>Due:</strong> {task['due']}</p>")

        if task.get('next'):
            body_lines.append(f"<p>➡️ <strong>Next:</strong> {task['next']}</p>")

        body_lines.extend([
            "<br>",
            "<p><strong>Status:</strong> ✅ Done</p>",
            f"<p><em>Created: {task.get('created_at', '')}</em></p>",
            f"<p><em>Completed: {datetime.fromisoformat(task['completed_at']).strftime('%Y-%m-%d %H:%M')}</em></p>",
            f"<p><em>ID: {task['id']}</em></p>",
        ])

        body = "<html><body>" + "".join(body_lines) + "</body></html>"

        # Escape for JXA
        note_id_esc = task['note_id'].replace('\\', '\\\\').replace('"', '\\"')
        body_esc = body.replace('\\', '\\\\').replace('"', '\\"')

        script = f"""
        const app = Application('Notes');

        try {{
            const note = app.notes.byId("{note_id_esc}");
            note.body = "{body_esc}";
            "success";
        }} catch (e) {{
            "error: " + e.message;
        }}
        """

        result = self._run_jxa(script)
        return result == "success"


# Convenience functions
_client = None

def get_client(folder='Tasks') -> AppleNotesClient:
    """Get or create singleton client."""
    global _client
    if _client is None:
        _client = AppleNotesClient(folder)
    return _client

def create_task(task: Dict) -> Dict:
    """Create task in Apple Notes."""
    return get_client().create_task(task)

def get_all_tasks() -> List[Dict]:
    """Get all tasks from Apple Notes."""
    return get_client().get_all_tasks()

def mark_done(task_id: str) -> bool:
    """Mark task as done."""
    return get_client().mark_done(task_id)
