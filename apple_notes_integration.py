"""Apple Notes integration using JXA (JavaScript for Automation).

This module provides functions to interact with Apple Notes on macOS using
osascript and JavaScript for Automation (JXA).

Requirements:
- macOS operating system
- Apple Notes app
- Python subprocess module (built-in)

Note: This integration uses osascript to execute JXA scripts, which means it
only works on macOS systems with Apple Notes installed.

References:
- JavaScript for Automation: https://developer.apple.com/library/archive/releasenotes/InterapplicationCommunication/RN-JavaScriptForAutomation/
- macOS Automation: http://www.macosxautomation.com/applescript/notes/index.html
"""

import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime


class AppleNotesClient:
    """Client for interacting with Apple Notes via JXA (JavaScript for Automation)."""

    def __init__(self):
        """Initialize the Apple Notes client."""
        self._check_macos()

    @staticmethod
    def _check_macos():
        """Check if running on macOS."""
        import platform
        if platform.system() != 'Darwin':
            raise RuntimeError(
                "Apple Notes integration only works on macOS. "
                f"Current system: {platform.system()}"
            )

    @staticmethod
    def _run_jxa_script(script: str) -> str:
        """Run a JXA script using osascript.

        Args:
            script: JXA script code

        Returns:
            Script output as string

        Raises:
            RuntimeError: If script execution fails
        """
        try:
            result = subprocess.run(
                ['osascript', '-l', 'JavaScript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"JXA script failed: {e.stderr}") from e
        except FileNotFoundError:
            raise RuntimeError(
                "osascript not found. This integration requires macOS."
            )

    def get_all_folders(self) -> List[Dict]:
        """Get all folders (accounts) in Apple Notes.

        Returns:
            List of folder dictionaries with 'name' and 'id' keys
        """
        script = """
        const app = Application('Notes');
        const accounts = app.accounts();
        const folders = [];

        for (let i = 0; i < accounts.length; i++) {
            const account = accounts[i];
            const accountFolders = account.folders();

            for (let j = 0; j < accountFolders.length; j++) {
                const folder = accountFolders[j];
                folders.push({
                    name: folder.name(),
                    id: folder.id(),
                    account: account.name()
                });
            }
        }

        JSON.stringify(folders);
        """
        result = self._run_jxa_script(script)
        return json.loads(result) if result else []

    def get_default_folder(self) -> Optional[str]:
        """Get the default folder for creating notes.

        Returns:
            Folder name (e.g., 'Notes') or None if not found
        """
        folders = self.get_all_folders()
        # Look for common default folder names
        for folder in folders:
            if folder['name'] in ['Notes', 'Tasks', 'Quick Notes']:
                return folder['name']
        # Return first folder if no default found
        return folders[0]['name'] if folders else None

    def create_note(
        self,
        title: str,
        body: str,
        folder: Optional[str] = None
    ) -> Dict:
        """Create a new note in Apple Notes.

        Args:
            title: Note title
            body: Note body content (plain text or HTML)
            folder: Folder name (defaults to 'Notes' folder in default account)

        Returns:
            Dict with note details including 'id', 'name', and 'creation_date'

        Example:
            client = AppleNotesClient()
            note = client.create_note(
                'My Task',
                'This is the task description\\nDue: Tomorrow'
            )
        """
        folder_name = folder or 'Notes'

        # Escape quotes and backslashes in text
        title_escaped = title.replace('\\', '\\\\').replace('"', '\\"')
        body_escaped = body.replace('\\', '\\\\').replace('"', '\\"')

        script = f"""
        const app = Application('Notes');
        const defaultAccount = app.defaultAccount();

        let targetFolder;
        try {{
            targetFolder = defaultAccount.folders.byName("{folder_name}");
        }} catch (e) {{
            // If folder doesn't exist, create it
            const newFolder = app.Folder({{name: "{folder_name}"}});
            defaultAccount.folders.push(newFolder);
            targetFolder = newFolder;
        }}

        const note = app.Note({{
            name: "{title_escaped}",
            body: "{body_escaped}"
        }});

        targetFolder.notes.push(note);

        JSON.stringify({{
            id: note.id(),
            name: note.name(),
            body: note.body(),
            creation_date: note.creationDate().toISOString(),
            modification_date: note.modificationDate().toISOString()
        }});
        """

        result = self._run_jxa_script(script)
        return json.loads(result) if result else {}

    def get_all_notes(self, folder: Optional[str] = None) -> List[Dict]:
        """Get all notes, optionally filtered by folder.

        Args:
            folder: Optional folder name to filter by

        Returns:
            List of note dictionaries with 'id', 'name', 'body', etc.
        """
        folder_filter = f'const folder = defaultAccount.folders.byName("{folder}");' if folder else ''
        notes_source = 'folder.notes()' if folder else 'app.notes()'

        script = f"""
        const app = Application('Notes');
        const defaultAccount = app.defaultAccount();
        {folder_filter}

        const notes = {notes_source};
        const result = [];

        for (let i = 0; i < notes.length; i++) {{
            const note = notes[i];
            result.push({{
                id: note.id(),
                name: note.name(),
                body: note.body().substring(0, 500), // Limit body preview
                creation_date: note.creationDate().toISOString(),
                modification_date: note.modificationDate().toISOString()
            }});
        }}

        JSON.stringify(result);
        """

        result = self._run_jxa_script(script)
        return json.loads(result) if result else []

    def find_notes_by_title(self, title: str) -> List[Dict]:
        """Find notes by title (case-insensitive partial match).

        Args:
            title: Title to search for

        Returns:
            List of matching note dictionaries
        """
        title_lower = title.lower()
        all_notes = self.get_all_notes()
        return [
            note for note in all_notes
            if title_lower in note['name'].lower()
        ]

    def get_note_by_id(self, note_id: str) -> Optional[Dict]:
        """Get a specific note by ID.

        Args:
            note_id: Note ID (from Notes app)

        Returns:
            Note dictionary or None if not found
        """
        script = f"""
        const app = Application('Notes');

        try {{
            const note = app.notes.byId("{note_id}");

            JSON.stringify({{
                id: note.id(),
                name: note.name(),
                body: note.body(),
                creation_date: note.creationDate().toISOString(),
                modification_date: note.modificationDate().toISOString()
            }});
        }} catch (e) {{
            JSON.stringify(null);
        }}
        """

        result = self._run_jxa_script(script)
        return json.loads(result) if result and result != 'null' else None

    def update_note(self, note_id: str, new_body: str) -> bool:
        """Update a note's body content.

        Args:
            note_id: Note ID
            new_body: New body content

        Returns:
            True if successful, False otherwise
        """
        body_escaped = new_body.replace('\\', '\\\\').replace('"', '\\"')

        script = f"""
        const app = Application('Notes');

        try {{
            const note = app.notes.byId("{note_id}");
            note.body = "{body_escaped}";
            "success";
        }} catch (e) {{
            "error: " + e.message;
        }}
        """

        result = self._run_jxa_script(script)
        return result == "success"

    def delete_note(self, note_id: str) -> bool:
        """Delete a note.

        Args:
            note_id: Note ID

        Returns:
            True if successful, False otherwise
        """
        script = f"""
        const app = Application('Notes');

        try {{
            const note = app.notes.byId("{note_id}");
            note.delete();
            "success";
        }} catch (e) {{
            "error: " + e.message;
        }}
        """

        result = self._run_jxa_script(script)
        return result == "success"

    def create_task_note(self, task: Dict, folder: str = "Tasks") -> Dict:
        """Create a formatted note for a task.

        Args:
            task: Task dictionary with title, owner, due_date, etc.
            folder: Folder to create note in (default: 'Tasks')

        Returns:
            Note dictionary with created note details
        """
        title = f"Task #{task.get('id', '?')}: {task['title']}"

        body_lines = [
            f"<h1>{task['title']}</h1>",
            f"<p><strong>Owner:</strong> {task.get('owner', 'N/A')}</p>",
        ]

        if task.get('due_date'):
            body_lines.append(f"<p><strong>Due:</strong> {task['due_date']}</p>")

        if task.get('next_step'):
            body_lines.append(f"<p><strong>Next Step:</strong> {task['next_step']}</p>")

        if task.get('status'):
            body_lines.append(f"<p><strong>Status:</strong> {task['status']}</p>")

        if task.get('notes'):
            body_lines.append(f"<p><strong>Notes:</strong></p><p>{task['notes']}</p>")

        body_lines.append(
            f"<p><em>Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}</em></p>"
        )

        body = "<html><body>" + "".join(body_lines) + "</body></html>"

        return self.create_note(title, body, folder)

    def sync_tasks_to_notes(
        self,
        tasks: List[Dict],
        folder: str = "Tasks",
        clear_existing: bool = False
    ) -> Dict:
        """Sync multiple tasks to Apple Notes.

        Args:
            tasks: List of task dictionaries
            folder: Folder to sync to (default: 'Tasks')
            clear_existing: If True, delete existing notes in folder before syncing

        Returns:
            Dict with sync statistics: {'created': int, 'errors': int}
        """
        stats = {'created': 0, 'errors': 0}

        # Optionally clear existing notes
        if clear_existing:
            existing_notes = self.get_all_notes(folder)
            for note in existing_notes:
                if note['name'].startswith('Task #'):
                    try:
                        self.delete_note(note['id'])
                    except:
                        pass

        # Create notes for each task
        for task in tasks:
            try:
                self.create_task_note(task, folder)
                stats['created'] += 1
            except Exception as e:
                stats['errors'] += 1
                print(f"Error creating note for task {task.get('id')}: {e}")

        return stats


# Convenience functions

def create_note(title: str, body: str, folder: Optional[str] = None) -> Dict:
    """Create a note in Apple Notes (convenience function).

    Args:
        title: Note title
        body: Note body
        folder: Optional folder name

    Returns:
        Note dictionary
    """
    client = AppleNotesClient()
    return client.create_note(title, body, folder)


def sync_tasks_to_apple_notes(tasks: List[Dict], folder: str = "Tasks") -> Dict:
    """Sync tasks to Apple Notes (convenience function).

    Args:
        tasks: List of task dictionaries
        folder: Folder name

    Returns:
        Sync statistics dictionary
    """
    client = AppleNotesClient()
    return client.sync_tasks_to_notes(tasks, folder)
