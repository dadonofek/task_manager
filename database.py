"""Database setup and management."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from config import Config

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT NOT NULL,
            due_date TEXT,
            next_step TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL,
            completed_at TEXT,
            notes TEXT
        )
    ''')

    # Task history table for tracking updates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    ''')

    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()

def add_task_history(task_id, action, details=None):
    """Add an entry to task history."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO task_history (task_id, action, details, timestamp) VALUES (?, ?, ?, ?)',
            (task_id, action, details, datetime.now().isoformat())
        )
        conn.commit()
