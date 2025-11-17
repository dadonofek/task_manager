"""Database migration script to add priority and category fields."""
import sqlite3
import sys
from config import Config


def migrate():
    """Add priority and category columns to tasks table."""
    print("🔄 Starting database migration...")

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Check if priority column exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cursor.fetchall()]

        migrations_applied = []

        # Add priority column if it doesn't exist
        if 'priority' not in columns:
            print("  Adding 'priority' column...")
            cursor.execute('''
                ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'
            ''')
            migrations_applied.append("priority")
            print("  ✅ Added 'priority' column")

        # Add category column if it doesn't exist
        if 'category' not in columns:
            print("  Adding 'category' column...")
            cursor.execute('''
                ALTER TABLE tasks ADD COLUMN category TEXT
            ''')
            migrations_applied.append("category")
            print("  ✅ Added 'category' column")

        if migrations_applied:
            conn.commit()
            print(f"\n✅ Migration complete! Added columns: {', '.join(migrations_applied)}")
        else:
            print("\n✅ Database is already up to date. No migrations needed.")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        conn.close()


def rollback():
    """Rollback migration by removing priority and category columns."""
    print("⚠️  Rolling back database migration...")
    print("Note: SQLite doesn't support dropping columns directly.")
    print("To rollback, you need to:")
    print("1. Delete the database file: rm tasks.db")
    print("2. Restart the app to recreate the old schema")
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback()
    else:
        migrate()
