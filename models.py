"""Task model and operations."""
from datetime import datetime
from typing import List, Optional, Dict
from database import get_db, add_task_history

class Task:
    """Task model."""

    def __init__(self, id=None, title='', owner='', due_date=None, next_step='',
                 status='open', created_at=None, completed_at=None, notes='',
                 priority='medium', category=None):
        self.id = id
        self.title = title
        self.owner = owner
        self.due_date = due_date
        self.next_step = next_step
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.notes = notes
        self.priority = priority
        self.category = category

    @staticmethod
    def _from_row(row) -> 'Task':
        """Create a Task object from a database row."""
        # sqlite3.Row doesn't have .get(), check if key exists
        def safe_get(row, key, default=None):
            try:
                return row[key]
            except (KeyError, IndexError):
                return default

        return Task(
            id=row['id'],
            title=row['title'],
            owner=row['owner'],
            due_date=row['due_date'],
            next_step=row['next_step'],
            status=row['status'],
            created_at=row['created_at'],
            completed_at=row['completed_at'],
            notes=row['notes'],
            priority=safe_get(row, 'priority', 'medium'),
            category=safe_get(row, 'category')
        )

    @staticmethod
    def create(title: str, owner: str, due_date: Optional[str] = None,
               next_step: Optional[str] = None, notes: Optional[str] = None,
               priority: str = 'medium', category: Optional[str] = None) -> int:
        """Create a new task and return its ID."""
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO tasks (title, owner, due_date, next_step, status, created_at, notes, priority, category)
                   VALUES (?, ?, ?, ?, 'open', ?, ?, ?, ?)''',
                (title, owner, due_date, next_step, datetime.now().isoformat(), notes, priority, category)
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
            return Task._from_row(row) if row else None

    @staticmethod
    def get_all_open() -> List['Task']:
        """Get all open tasks, sorted by priority (high first), then due date."""
        with get_db() as conn:
            cursor = conn.cursor()
            # Sort by priority (high=0, medium=1, low=2), then due_date
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = "open"
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 0
                        WHEN 'medium' THEN 1
                        WHEN 'low' THEN 2
                        ELSE 1
                    END,
                    due_date, id
            ''')
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

    @staticmethod
    def get_by_owner(owner: str) -> List['Task']:
        """Get all open tasks for a specific owner, sorted by priority."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tasks
                WHERE owner = ? AND status = "open"
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 0
                        WHEN 'medium' THEN 1
                        WHEN 'low' THEN 2
                        ELSE 1
                    END,
                    due_date, id
            ''', (owner,))
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

    @staticmethod
    def get_today() -> List['Task']:
        """Get all tasks due today, sorted by priority."""
        today = datetime.now().strftime('%Y-%m-%d')
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = "open" AND due_date LIKE ?
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 0
                        WHEN 'medium' THEN 1
                        WHEN 'low' THEN 2
                        ELSE 1
                    END,
                    due_date, id
            ''', (f'{today}%',))
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

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

    @staticmethod
    def update_priority(task_id: int, priority: str) -> bool:
        """Update the priority of a task."""
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET priority = ? WHERE id = ?',
                (priority, task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'priority_changed', f'Priority changed to: {priority}')
                return True
            return False

    @staticmethod
    def update_category(task_id: int, category: Optional[str]) -> bool:
        """Update the category of a task."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE tasks SET category = ? WHERE id = ?',
                (category, task_id)
            )
            conn.commit()

            if cursor.rowcount > 0:
                add_task_history(task_id, 'category_changed', f'Category changed to: {category}')
                return True
            return False

    @staticmethod
    def get_by_priority(priority: str) -> List['Task']:
        """Get all open tasks with a specific priority."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = "open" AND priority = ?
                ORDER BY due_date, id
            ''', (priority,))
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

    @staticmethod
    def get_by_category(category: str) -> List['Task']:
        """Get all open tasks with a specific category."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = "open" AND category = ?
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 0
                        WHEN 'medium' THEN 1
                        WHEN 'low' THEN 2
                        ELSE 1
                    END,
                    due_date, id
            ''', (category,))
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

    @staticmethod
    def get_by_filters(owner: Optional[str] = None, priority: Optional[str] = None,
                       category: Optional[str] = None, status: str = 'open') -> List['Task']:
        """Get tasks filtered by owner, priority, and/or category."""
        with get_db() as conn:
            cursor = conn.cursor()

            # Build dynamic query
            conditions = ['status = ?']
            params = [status]

            if owner:
                conditions.append('owner = ?')
                params.append(owner)

            if priority:
                conditions.append('priority = ?')
                params.append(priority)

            if category:
                conditions.append('category = ?')
                params.append(category)

            where_clause = ' AND '.join(conditions)

            query = f'''
                SELECT * FROM tasks
                WHERE {where_clause}
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 0
                        WHEN 'medium' THEN 1
                        WHEN 'low' THEN 2
                        ELSE 1
                    END,
                    due_date, id
            '''

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Task._from_row(row) for row in rows]

    @staticmethod
    def get_all_categories() -> List[str]:
        """Get list of all categories in use."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT category FROM tasks
                WHERE category IS NOT NULL
                ORDER BY category
            ''')
            rows = cursor.fetchall()
            return [row['category'] for row in rows]

    @staticmethod
    def get_history(task_id: int) -> List[Dict]:
        """Get the history of changes for a task."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_history
                WHERE task_id = ?
                ORDER BY timestamp DESC
            ''', (task_id,))
            rows = cursor.fetchall()
            return [{
                'id': row['id'],
                'task_id': row['task_id'],
                'action': row['action'],
                'details': row['details'],
                'timestamp': row['timestamp']
            } for row in rows]

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
            'notes': self.notes,
            'priority': self.priority,
            'category': self.category
        }
