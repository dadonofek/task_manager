"""Example usage of WhatsApp integration.

This script demonstrates how to use the WhatsApp integration
to send messages and task notifications.

Before running:
1. Set environment variables: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
2. Join the Twilio WhatsApp Sandbox
3. Update RECIPIENT_NUMBER with your phone number
"""

import os
from whatsapp_integration import WhatsAppClient, send_whatsapp_message, send_task_update
from models import Task

# Configuration
RECIPIENT_NUMBER = '+1234567890'  # Change this to your phone number!


def example_1_simple_message():
    """Example 1: Send a simple WhatsApp message."""
    print("\n=== Example 1: Simple Message ===")

    client = WhatsAppClient()

    result = client.send_message(
        to_number=RECIPIENT_NUMBER,
        body='Hello! This is a test message from your Task Manager.'
    )

    print(f"Message sent! SID: {result['sid']}")
    print(f"Status: {result['status']}")


def example_2_task_notification():
    """Example 2: Send a task notification."""
    print("\n=== Example 2: Task Notification ===")

    # Create a sample task
    task = {
        'id': 123,
        'title': 'Review quarterly reports',
        'owner': 'Ofek',
        'due_date': '2024-01-20 17:00',
        'next_step': 'Download from shared drive',
        'status': 'open',
        'notes': 'Focus on Q4 sales figures'
    }

    action_urls = {
        'mark_done': 'https://your-app.com/markDone/123',
        'view_task': 'https://your-app.com/task/123'
    }

    client = WhatsAppClient()
    result = client.send_task_notification(
        to_number=RECIPIENT_NUMBER,
        task=task,
        action_urls=action_urls
    )

    print(f"Task notification sent! SID: {result['sid']}")


def example_3_task_list():
    """Example 3: Send a list of tasks."""
    print("\n=== Example 3: Task List ===")

    tasks = [
        {
            'id': 1,
            'title': 'Upload medical docs',
            'owner': 'Wife',
            'due_date': '2024-01-18 20:00',
            'next_step': 'Scan documents'
        },
        {
            'id': 2,
            'title': 'Review contract',
            'owner': 'Ofek',
            'due_date': '2024-01-19 15:00',
            'next_step': 'Schedule call with lawyer'
        },
        {
            'id': 3,
            'title': 'Book flight tickets',
            'owner': 'Ofek',
            'due_date': None,
            'next_step': 'Check dates'
        }
    ]

    client = WhatsAppClient()
    result = client.send_task_list(
        to_number=RECIPIENT_NUMBER,
        tasks=tasks,
        title='Your Open Tasks'
    )

    print(f"Task list sent! SID: {result['sid']}")


def example_4_send_with_media():
    """Example 4: Send a message with an image."""
    print("\n=== Example 4: Message with Media ===")

    client = WhatsAppClient()

    result = client.send_message(
        to_number=RECIPIENT_NUMBER,
        body='Here is your task dashboard screenshot!',
        media_url='https://picsum.photos/800/600'  # Example image URL
    )

    print(f"Message with media sent! SID: {result['sid']}")


def example_5_convenience_functions():
    """Example 5: Using convenience functions."""
    print("\n=== Example 5: Convenience Functions ===")

    # Simple message using convenience function
    result1 = send_whatsapp_message(
        to_number=RECIPIENT_NUMBER,
        body='Quick message via convenience function!'
    )
    print(f"Message sent via convenience function: {result1['sid']}")

    # Task update using convenience function
    task = {
        'id': 456,
        'title': 'Prepare presentation',
        'owner': 'Ofek',
        'status': 'in_progress'
    }

    result2 = send_task_update(
        to_number=RECIPIENT_NUMBER,
        task=task
    )
    print(f"Task update sent via convenience function: {result2['sid']}")


def example_6_notify_from_database():
    """Example 6: Send notification for a real task from database."""
    print("\n=== Example 6: Database Task Notification ===")

    # Get first open task from database
    tasks = Task.get_all_open()

    if not tasks:
        print("No open tasks found in database!")
        return

    task = tasks[0]
    client = WhatsAppClient()

    result = client.send_task_notification(
        to_number=RECIPIENT_NUMBER,
        task=task.to_dict()
    )

    print(f"Sent notification for task #{task.id}: {task.title}")
    print(f"Message SID: {result['sid']}")


def main():
    """Run all examples."""
    print("WhatsApp Integration Examples")
    print("=" * 50)

    # Check if credentials are set
    if not os.getenv('TWILIO_ACCOUNT_SID') or not os.getenv('TWILIO_AUTH_TOKEN'):
        print("\n❌ Error: Twilio credentials not set!")
        print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")
        return

    # Check if recipient number is configured
    if RECIPIENT_NUMBER == '+1234567890':
        print("\n⚠️  Warning: Using default recipient number!")
        print("Please update RECIPIENT_NUMBER in this script with your phone number.")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    try:
        # Run examples
        example_1_simple_message()
        example_2_task_notification()
        example_3_task_list()
        example_4_send_with_media()
        example_5_convenience_functions()

        # Uncomment to test with real database
        # example_6_notify_from_database()

        print("\n✅ All examples completed successfully!")
        print("\nCheck your WhatsApp to see the messages.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you:")
        print("1. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables")
        print("2. Joined the WhatsApp Sandbox")
        print("3. Updated RECIPIENT_NUMBER with your phone number")


if __name__ == '__main__':
    main()
