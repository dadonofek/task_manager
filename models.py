"""Task model and operations."""
from datetime import datetime
from typing import List, Optional, Dict
from database import get_db, add_task_history

class Task:
    """Task model."""

    def __init__(self, id=None, title='', owner='', due_date=None, next_step='',
                 status='open', created_at=None, completed_at=None, notes=''):
        self.id = id
        self.title = title
        self.owner = owner
        self.due_date = due_date
        self.next_step = next_step
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.notes = notes

    @staticmethod
    def create(title: str, owner: str, due_date: Optional[str] = None,
               next_step: Optional[str] = None, notes: Optional[str] = None) -> int:
        """Create a new task and return its ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO tasks (title, owner, due_date, next_step, status, created_at, notes)
                   VALUES (?, ?, ?, ?, 'open', ?, ?)''',
                (title, owner, due_date, next_step, datetime.now().isoformat(), notes)
            )
            conn.commit()
            task_id = cursor.lastrowid

            # Add to history
            add_task_history(task_id, 'created', f'Task created: {title}')

            return task_id

    @staticmethod
    def get_by_id(task_id: int) -> Optional['Task']:
        """Get a task by ID."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()

            if row:
                return Task(
                    id=row['id'],
                    title=row['title'],
                    owner=row['owner'],
                    due_date=row['due_date'],
                    next_step=row['next_step'],
                    status=row['status'],
                    created_at=row['created_at'],
                    completed_at=row['completed_at'],
                    notes=row['notes']
                )
            return None

    @staticmethod
    def get_all_open() -> List['Task']:
        """Get all open tasks."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE status = "open" ORDER BY due_date, id')
            rows = cursor.fetchall()

            return [Task(
                id=row['id'],
                title=row['title'],
                owner=row['owner'],
                due_date=row['due_date'],
                next_step=row['next_step'],
                status=row['status'],
                created_at=row['created_at'],
                completed_at=row['completed_at'],
                notes=row['notes']
            ) for row in rows]

    @staticmethod
    def get_by_owner(owner: str) -> List['Task']:
        """Get all open tasks for a specific owner."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM tasks WHERE owner = ? AND status = "open" ORDER BY due_date, id',
                (owner,)
            )
            rows = cursor.fetchall()

            return [Task(
                id=row['id'],
                title=row['title'],
                owner=row['owner'],
                due_date=row['due_date'],
                next_step=row['next_step'],
                status=row['status'],
                created_at=row['created_at'],
                completed_at=row['completed_at'],
                notes=row['notes']
            ) for row in rows]

    @staticmethod
    def get_today() -> List['Task']:
        """Get all tasks due today."""
        today = datetime.now().strftime('%Y-%m-%d')
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM tasks
                   WHERE status = "open" AND due_date LIKE ?
                   ORDER BY due_date, id''',
                (f'{today}%',)
            )
            rows = cursor.fetchall()

            return [Task(
                id=row['id'],
                title=row['title'],
                owner=row['owner'],
                due_date=row['due_date'],
                next_step=row['next_step'],
                status=row['status'],
                created_at=row['created_at'],
                completed_at=row['completed_at'],
                notes=row['notes']
            ) for row in rows]

    @staticmethod
    def mark_done(task_id: int) -> bool:
        """Mark a task as done."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET status = "done", completed_at = ? WHERE id = ?',
                (datetime.now().isoformat(), task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'completed', 'Task marked as done')
                return True
            return False

    @staticmethod
    def reassign(task_id: int, new_owner: str) -> bool:
        """Reassign a task to a new owner."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET owner = ? WHERE id = ?',
                (new_owner, task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'reassigned', f'Reassigned to {new_owner}')
                return True
            return False

    @staticmethod
    def update_due_date(task_id: int, new_due_date: str) -> bool:
        """Update the due date of a task."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET due_date = ? WHERE id = ?',
                (new_due_date, task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'due_date_changed', f'New due date: {new_due_date}')
                return True
            return False

    @staticmethod
    def update_next_step(task_id: int, next_step: str) -> bool:
        """Update the next step of a task."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET next_step = ? WHERE id = ?',
                (next_step, task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'next_step_updated', f'Next step: {next_step}')
                return True
            return False

    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'owner': self.owner,
            'due_date': self.due_date,
            'next_step': self.next_step,
            'status': self.status,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'notes': self.notes
        }
