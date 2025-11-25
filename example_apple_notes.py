"""Example usage of Apple Notes integration.

This script demonstrates how to use the Apple Notes integration
to create, read, update, and sync tasks.

Requirements:
- macOS operating system
- Apple Notes app installed
- Python 3.6+

Note: This will create real notes in your Apple Notes app!
"""

from apple_notes_integration import AppleNotesClient, create_note, sync_tasks_to_apple_notes
from models import Task
from datetime import datetime


def example_1_check_folders():
    """Example 1: List all folders in Apple Notes."""
    print("\n=== Example 1: List Folders ===")

    client = AppleNotesClient()
    folders = client.get_all_folders()

    print(f"Found {len(folders)} folders:")
    for folder in folders:
        print(f"  - {folder['name']} (Account: {folder['account']})")

    default = client.get_default_folder()
    print(f"\nDefault folder: {default}")


def example_2_create_simple_note():
    """Example 2: Create a simple note."""
    print("\n=== Example 2: Create Simple Note ===")

    client = AppleNotesClient()

    note = client.create_note(
        title='My First Note',
        body='This is a test note created via Python!',
        folder='Notes'
    )

    print(f"Created note: {note['name']}")
    print(f"Note ID: {note['id']}")
    print(f"Created at: {note['creation_date']}")


def example_3_create_formatted_note():
    """Example 3: Create a note with HTML formatting."""
    print("\n=== Example 3: Create Formatted Note ===")

    client = AppleNotesClient()

    html_body = """
    <html>
    <body>
        <h1>Project Meeting Notes</h1>
        <p><strong>Date:</strong> January 15, 2024</p>
        <p><strong>Attendees:</strong> Ofek, Sarah, Mike</p>

        <h2>Agenda</h2>
        <ul>
            <li>Review Q4 results</li>
            <li>Discuss 2024 roadmap</li>
            <li>Budget allocation</li>
        </ul>

        <h2>Action Items</h2>
        <ol>
            <li>Ofek: Prepare budget proposal</li>
            <li>Sarah: Schedule follow-up meeting</li>
            <li>Mike: Review technical requirements</li>
        </ol>
    </body>
    </html>
    """

    note = client.create_note(
        title='Meeting Notes - Jan 15',
        body=html_body,
        folder='Notes'
    )

    print(f"Created formatted note: {note['name']}")


def example_4_list_notes():
    """Example 4: List all notes."""
    print("\n=== Example 4: List Notes ===")

    client = AppleNotesClient()

    # Get all notes
    all_notes = client.get_all_notes()
    print(f"Total notes: {len(all_notes)}")

    # Show first 5 notes
    print("\nFirst 5 notes:")
    for note in all_notes[:5]:
        print(f"  - {note['name']}")
        print(f"    Created: {note['creation_date']}")
        print(f"    Preview: {note['body'][:100]}...")
        print()


def example_5_search_notes():
    """Example 5: Search notes by title."""
    print("\n=== Example 5: Search Notes ===")

    client = AppleNotesClient()

    search_term = 'task'
    matching_notes = client.find_notes_by_title(search_term)

    print(f"Found {len(matching_notes)} notes matching '{search_term}':")
    for note in matching_notes:
        print(f"  - {note['name']}")


def example_6_create_task_note():
    """Example 6: Create a formatted task note."""
    print("\n=== Example 6: Create Task Note ===")

    client = AppleNotesClient()

    task = {
        'id': 999,
        'title': 'Complete project proposal',
        'owner': 'Ofek',
        'due_date': '2024-01-25 17:00',
        'next_step': 'Review requirements document',
        'status': 'open',
        'notes': 'High priority - client meeting next week'
    }

    note = client.create_task_note(task, folder='Tasks')

    print(f"Created task note: {note['name']}")
    print(f"Note ID: {note['id']}")


def example_7_sync_tasks():
    """Example 7: Sync all open tasks to Apple Notes."""
    print("\n=== Example 7: Sync Tasks to Apple Notes ===")

    # Get all open tasks from database
    tasks = Task.get_all_open()

    if not tasks:
        print("No open tasks found in database!")
        print("\nCreating sample tasks for demonstration...")

        # Create sample tasks
        sample_tasks = [
            {
                'id': 1001,
                'title': 'Review quarterly reports',
                'owner': 'Ofek',
                'due_date': '2024-01-20 17:00',
                'next_step': 'Download from shared drive',
                'status': 'open'
            },
            {
                'id': 1002,
                'title': 'Prepare presentation',
                'owner': 'Sarah',
                'due_date': '2024-01-22 14:00',
                'next_step': 'Create slide deck',
                'status': 'open'
            },
            {
                'id': 1003,
                'title': 'Update documentation',
                'owner': 'Mike',
                'due_date': None,
                'next_step': 'Review API changes',
                'status': 'open'
            }
        ]
        tasks_to_sync = sample_tasks
    else:
        tasks_to_sync = [task.to_dict() for task in tasks]

    print(f"Syncing {len(tasks_to_sync)} tasks to Apple Notes...")

    client = AppleNotesClient()
    stats = client.sync_tasks_to_notes(
        tasks=tasks_to_sync,
        folder='Tasks',
        clear_existing=False  # Don't delete existing notes
    )

    print(f"\n✅ Sync completed!")
    print(f"   Created: {stats['created']} notes")
    print(f"   Errors: {stats['errors']}")


def example_8_update_note():
    """Example 8: Update an existing note."""
    print("\n=== Example 8: Update Note ===")

    client = AppleNotesClient()

    # Find a note to update
    notes = client.find_notes_by_title('My First Note')

    if not notes:
        print("Note 'My First Note' not found. Run example_2 first!")
        return

    note = notes[0]
    note_id = note['id']

    print(f"Updating note: {note['name']}")

    new_content = f"""
    <html>
    <body>
        <h1>Updated Note</h1>
        <p>This note was updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> Modified</p>
    </body>
    </html>
    """

    success = client.update_note(note_id, new_content)

    if success:
        print("✅ Note updated successfully!")
    else:
        print("❌ Failed to update note")


def example_9_get_specific_note():
    """Example 9: Get a specific note by ID."""
    print("\n=== Example 9: Get Specific Note ===")

    client = AppleNotesClient()

    # First, find a note
    notes = client.get_all_notes()

    if not notes:
        print("No notes found!")
        return

    note_id = notes[0]['id']
    print(f"Fetching note with ID: {note_id}")

    note = client.get_note_by_id(note_id)

    if note:
        print(f"\nNote details:")
        print(f"  Title: {note['name']}")
        print(f"  Created: {note['creation_date']}")
        print(f"  Modified: {note['modification_date']}")
        print(f"  Body preview: {note['body'][:200]}...")
    else:
        print("Note not found!")


def example_10_convenience_function():
    """Example 10: Using convenience functions."""
    print("\n=== Example 10: Convenience Functions ===")

    # Create note using convenience function
    note = create_note(
        title='Quick Note',
        body='Created via convenience function!',
        folder='Notes'
    )

    print(f"Created note: {note['name']}")

    # Sync using convenience function (with sample data)
    sample_tasks = [
        {
            'id': 2001,
            'title': 'Sample task',
            'owner': 'Ofek',
            'status': 'open'
        }
    ]

    stats = sync_tasks_to_apple_notes(sample_tasks, folder='Tasks')
    print(f"Synced {stats['created']} tasks")


def main():
    """Run all examples."""
    print("Apple Notes Integration Examples")
    print("=" * 50)
    print("\n⚠️  Warning: This will create notes in your Apple Notes app!")
    print("Make sure you're running this on macOS with Apple Notes installed.\n")

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    try:
        # Run examples
        example_1_check_folders()
        example_2_create_simple_note()
        example_3_create_formatted_note()
        example_4_list_notes()
        example_5_search_notes()
        example_6_create_task_note()
        example_7_sync_tasks()
        example_8_update_note()
        example_9_get_specific_note()
        example_10_convenience_function()

        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\nCheck your Apple Notes app to see the created notes.")
        print("You can safely delete them if you don't need them.")

    except RuntimeError as e:
        if "macOS" in str(e):
            print(f"\n❌ Error: {e}")
            print("\nThis integration only works on macOS.")
            print("If you're on Linux/Windows, you can only use the WhatsApp integration.")
        else:
            raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. You're running on macOS")
        print("2. Apple Notes app is installed")
        print("3. You have the necessary permissions")


if __name__ == '__main__':
    main()
