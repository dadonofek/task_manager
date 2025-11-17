"""Basic test script to verify the application works."""
import os
from database import init_db
from models import Task

def test_basic_workflow():
    """Test the basic task workflow."""
    print("🧪 Testing WhatsApp Task Manager...\n")

    # Clean up if database exists
    if os.path.exists('test_tasks.db'):
        os.remove('test_tasks.db')

    # Initialize database
    os.environ['DATABASE_PATH'] = 'test_tasks.db'
    from config import Config
    Config.DATABASE_PATH = 'test_tasks.db'
    init_db()
    print("✅ Database initialized")

    # Create tasks
    task1_id = Task.create(
        title="Buy groceries",
        owner="Ofek",
        due_date="2024-01-20 18:00",
        next_step="Get milk and bread"
    )
    print(f"✅ Created task #{task1_id}: Buy groceries")

    task2_id = Task.create(
        title="Call dentist",
        owner="Wife",
        due_date="2024-01-21 14:00",
        next_step="Book appointment"
    )
    print(f"✅ Created task #{task2_id}: Call dentist")

    task3_id = Task.create(
        title="Upload documents",
        owner="Ofek",
        due_date="2024-01-20 20:00",
        next_step="Wife reviews"
    )
    print(f"✅ Created task #{task3_id}: Upload documents")

    # Get all open tasks
    open_tasks = Task.get_all_open()
    print(f"\n📋 Open tasks: {len(open_tasks)}")
    for task in open_tasks:
        print(f"   - #{task.id}: {task.title} (Owner: {task.owner})")

    # Get tasks by owner
    ofek_tasks = Task.get_by_owner("Ofek")
    print(f"\n👤 Ofek's tasks: {len(ofek_tasks)}")
    for task in ofek_tasks:
        print(f"   - #{task.id}: {task.title}")

    # Mark a task as done
    Task.mark_done(task1_id)
    print(f"\n✅ Marked task #{task1_id} as done")

    # Verify it's done
    task1 = Task.get_by_id(task1_id)
    assert task1.status == 'done', "Task should be marked as done"
    print(f"   Status: {task1.status}")

    # Verify open tasks count decreased
    open_tasks = Task.get_all_open()
    assert len(open_tasks) == 2, "Should have 2 open tasks now"
    print(f"\n📋 Open tasks after completion: {len(open_tasks)}")

    # Reassign a task
    Task.reassign(task2_id, "Ofek")
    task2 = Task.get_by_id(task2_id)
    assert task2.owner == "Ofek", "Task should be reassigned to Ofek"
    print(f"\n🔄 Reassigned task #{task2_id} to {task2.owner}")

    # Update due date
    Task.update_due_date(task3_id, "2024-01-22 10:00")
    task3 = Task.get_by_id(task3_id)
    print(f"\n📅 Updated task #{task3_id} due date to {task3.due_date}")

    # Update next step
    Task.update_next_step(task3_id, "Ofek submits final version")
    task3 = Task.get_by_id(task3_id)
    print(f"\n➡️  Updated task #{task3_id} next step: {task3.next_step}")

    print("\n✅ All tests passed!")
    print(f"\n💾 Test database: test_tasks.db")
    print("   You can inspect it with: sqlite3 test_tasks.db")

    # Clean up
    # os.remove('test_tasks.db')
    # print("\n🧹 Cleaned up test database")

if __name__ == '__main__':
    test_basic_workflow()
