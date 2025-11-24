"""Main Flask application for WhatsApp Task Manager."""
from flask import Flask, request, jsonify, render_template, redirect, url_for, Response
from datetime import datetime
from dateutil import parser as date_parser
import re
from database import init_db
from models import Task
from config import Config
from whatsapp_integration import WhatsAppClient

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
init_db()


def parse_whatsapp_task(text: str) -> dict:
    """Parse a WhatsApp task creation message.

    Expected format:
    #task
    Title: Upload medical docs
    Owner: Wife
    Due: Thu 20:00
    Next: Ofek submits
    """
    lines = text.strip().split('\n')
    task_data = {}

    for line in lines:
        line = line.strip()
        if line.startswith('#task'):
            continue

        # Parse key-value pairs
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()

            if key == 'title':
                task_data['title'] = value
            elif key == 'owner':
                task_data['owner'] = value
            elif key == 'due':
                task_data['due_date'] = parse_due_date(value)
            elif key == 'next':
                task_data['next_step'] = value

    return task_data


def parse_due_date(due_str: str) -> str:
    """Parse a due date string into ISO format.

    Handles formats like:
    - Thu 20:00
    - 2024-01-15 20:00
    - Jan 15 8pm
    """
    try:
        # Try parsing as full datetime
        dt = date_parser.parse(due_str, fuzzy=True)
        return dt.isoformat()
    except:
        # Return as-is if parsing fails
        return due_str


def generate_quick_actions(task_id: int) -> dict:
    """Generate quick action URLs for a task."""
    base = Config.BASE_URL
    return {
        'mark_done': f'{base}/markDone/{task_id}',
        'reassign_ofek': f'{base}/reassign/{task_id}?to=Ofek',
        'reassign_wife': f'{base}/reassign/{task_id}?to=Wife',
        'view_task': f'{base}/task/{task_id}',
    }


# ============================================================================
# Web UI Routes
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to open tasks."""
    return redirect(url_for('open_tasks'))


@app.route('/open')
def open_tasks():
    """View all open tasks."""
    tasks = Task.get_all_open()
    return render_template('open.html', tasks=tasks, base_url=Config.BASE_URL)


@app.route('/mine')
def my_tasks():
    """View tasks for a specific owner."""
    owner = request.args.get('owner', 'Ofek')
    tasks = Task.get_by_owner(owner)
    return render_template('mine.html', tasks=tasks, owner=owner, base_url=Config.BASE_URL)


@app.route('/today')
def today_tasks():
    """View tasks due today."""
    tasks = Task.get_today()
    return render_template('today.html', tasks=tasks, base_url=Config.BASE_URL)


@app.route('/task/<int:task_id>')
def view_task(task_id):
    """View a single task with quick actions."""
    task = Task.get_by_id(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    actions = generate_quick_actions(task_id)
    return render_template('task.html', task=task, actions=actions, base_url=Config.BASE_URL)


# ============================================================================
# API Routes - Task Management
# ============================================================================

@app.route('/api/newTask', methods=['POST'])
def create_task_api():
    """Create a new task via API.

    Expects JSON:
    {
        "title": "Task title",
        "owner": "Owner name",
        "due_date": "2024-01-15 20:00",  // optional
        "next_step": "Next step",         // optional
        "notes": "Additional notes"       // optional
    }
    """
    data = request.get_json()

    if not data or 'title' not in data or 'owner' not in data:
        return jsonify({'error': 'Missing required fields: title, owner'}), 400

    task_id = Task.create(
        title=data['title'],
        owner=data['owner'],
        due_date=data.get('due_date'),
        next_step=data.get('next_step'),
        notes=data.get('notes')
    )

    actions = generate_quick_actions(task_id)

    return jsonify({
        'success': True,
        'task_id': task_id,
        'message': f'Task #{task_id} created successfully',
        'quick_actions': actions
    }), 201


@app.route('/newTask', methods=['GET', 'POST'])
def create_task():
    """Create a new task from WhatsApp format or form.

    GET with ?text= parameter: Parse WhatsApp format
    POST: Create from form data
    """
    if request.method == 'GET':
        # Parse WhatsApp format from query parameter
        text = request.args.get('text', '')
        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400

        task_data = parse_whatsapp_task(text)

        if not task_data.get('title') or not task_data.get('owner'):
            return jsonify({'error': 'Could not parse task. Missing title or owner.'}), 400

        task_id = Task.create(**task_data)
        actions = generate_quick_actions(task_id)

        return render_template('task_created.html',
                             task_id=task_id,
                             task_data=task_data,
                             actions=actions,
                             base_url=Config.BASE_URL)

    # POST - form submission
    task_id = Task.create(
        title=request.form['title'],
        owner=request.form['owner'],
        due_date=request.form.get('due_date'),
        next_step=request.form.get('next_step'),
        notes=request.form.get('notes')
    )

    return redirect(url_for('view_task', task_id=task_id))


@app.route('/markDone/<int:task_id>', methods=['GET', 'POST'])
def mark_done(task_id):
    """Mark a task as done."""
    success = Task.mark_done(task_id)

    if not success:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'GET':
        return render_template('action_success.html',
                             message=f'Task #{task_id} marked as done!',
                             redirect_url=url_for('open_tasks'))

    return jsonify({'success': True, 'message': f'Task #{task_id} marked as done'})


@app.route('/reassign/<int:task_id>', methods=['GET', 'POST'])
def reassign_task(task_id):
    """Reassign a task to a new owner."""
    new_owner = request.args.get('to') or request.form.get('to')

    if not new_owner:
        return jsonify({'error': 'Missing "to" parameter'}), 400

    success = Task.reassign(task_id, new_owner)

    if not success:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'GET':
        return render_template('action_success.html',
                             message=f'Task #{task_id} reassigned to {new_owner}!',
                             redirect_url=url_for('open_tasks'))

    return jsonify({'success': True, 'message': f'Task reassigned to {new_owner}'})


@app.route('/updateDue/<int:task_id>', methods=['GET', 'POST'])
def update_due_date(task_id):
    """Update the due date of a task."""
    new_due = request.args.get('date') or request.form.get('date')

    if not new_due:
        return jsonify({'error': 'Missing "date" parameter'}), 400

    # Parse the date
    new_due = parse_due_date(new_due)

    success = Task.update_due_date(task_id, new_due)

    if not success:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'GET':
        return render_template('action_success.html',
                             message=f'Task #{task_id} due date updated!',
                             redirect_url=url_for('view_task', task_id=task_id))

    return jsonify({'success': True, 'message': f'Due date updated'})


@app.route('/updateNext/<int:task_id>', methods=['GET', 'POST'])
def update_next_step(task_id):
    """Update the next step of a task."""
    next_step = request.args.get('step') or request.form.get('step')

    if not next_step:
        return jsonify({'error': 'Missing "step" parameter'}), 400

    success = Task.update_next_step(task_id, next_step)

    if not success:
        return jsonify({'error': 'Task not found'}), 404

    if request.method == 'GET':
        return render_template('action_success.html',
                             message=f'Task #{task_id} next step updated!',
                             redirect_url=url_for('view_task', task_id=task_id))

    return jsonify({'success': True, 'message': f'Next step updated'})


# ============================================================================
# API Routes - Data Access
# ============================================================================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks or filter by status/owner."""
    status = request.args.get('status')
    owner = request.args.get('owner')

    if owner:
        tasks = Task.get_by_owner(owner)
    elif status == 'open':
        tasks = Task.get_all_open()
    else:
        tasks = Task.get_all_open()

    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    })


@app.route('/api/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    task = Task.get_by_id(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task.to_dict())


# ============================================================================
# WhatsApp Webhook Integration
# ============================================================================

@app.route('/whatsapp/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio.

    This endpoint receives webhooks from Twilio when users send WhatsApp messages.

    Configure this URL in your Twilio WhatsApp Sandbox settings:
    https://your-domain.com/whatsapp/webhook
    """
    try:
        # Parse incoming message
        incoming_msg = WhatsAppClient.parse_incoming_message(request.form.to_dict())

        from_number = incoming_msg['from_number']
        body = incoming_msg['body'].lower()

        # Handle different commands
        if body.startswith('#task'):
            # Create new task from WhatsApp format
            task_data = parse_whatsapp_task(incoming_msg['body'])

            if task_data.get('title') and task_data.get('owner'):
                task_id = Task.create(**task_data)
                actions = generate_quick_actions(task_id)

                response_text = f"✓ Task #{task_id} created!\n\n"
                response_text += f"Title: {task_data['title']}\n"
                response_text += f"Owner: {task_data['owner']}\n"
                if task_data.get('due_date'):
                    response_text += f"Due: {task_data['due_date']}\n"
                response_text += f"\nView: {actions['view_task']}"
            else:
                response_text = "❌ Could not create task. Please include Title and Owner."

        elif body == 'my tasks' or body == 'mytasks':
            # List user's tasks (assumes default owner 'Ofek')
            owner = request.args.get('owner', 'Ofek')
            tasks = Task.get_by_owner(owner)

            if tasks:
                response_text = f"*Your Open Tasks ({len(tasks)}):*\n\n"
                for task in tasks[:5]:  # Limit to 5 tasks
                    response_text += f"• {task.title}\n"
                    if task.due_date:
                        response_text += f"  Due: {task.due_date}\n"
            else:
                response_text = "You have no open tasks! 🎉"

        elif body == 'today':
            # List today's tasks
            tasks = Task.get_today()

            if tasks:
                response_text = f"*Tasks Due Today ({len(tasks)}):*\n\n"
                for task in tasks:
                    response_text += f"• {task.title} ({task.owner})\n"
            else:
                response_text = "No tasks due today! ✨"

        elif body == 'help':
            response_text = """*Task Manager Commands:*

📝 Create Task:
#task
Title: Your task
Owner: Name
Due: Thu 20:00

📋 View Tasks:
• "my tasks" - your tasks
• "today" - today's tasks

❓ "help" - show this menu"""

        else:
            response_text = "Send 'help' to see available commands."

        # Create TwiML response
        response_xml = WhatsAppClient.create_response(response_text)
        return Response(response_xml, mimetype='text/xml')

    except Exception as e:
        # Log error and send friendly response
        print(f"Error in WhatsApp webhook: {e}")
        response_xml = WhatsAppClient.create_response(
            "Sorry, something went wrong. Please try again."
        )
        return Response(response_xml, mimetype='text/xml')


@app.route('/whatsapp/send', methods=['POST'])
def whatsapp_send():
    """Send a WhatsApp message programmatically.

    POST JSON:
    {
        "to": "+1234567890",
        "body": "Your message",
        "media_url": "https://..." (optional)
    }
    """
    try:
        data = request.get_json()

        if not data or 'to' not in data or 'body' not in data:
            return jsonify({'error': 'Missing required fields: to, body'}), 400

        client = WhatsAppClient()
        result = client.send_message(
            to_number=data['to'],
            body=data['body'],
            media_url=data.get('media_url')
        )

        return jsonify({
            'success': True,
            'message': 'WhatsApp message sent',
            'details': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/whatsapp/notify/<int:task_id>', methods=['POST'])
def whatsapp_notify_task(task_id):
    """Send a WhatsApp notification for a specific task.

    POST JSON:
    {
        "to": "+1234567890"
    }
    """
    try:
        data = request.get_json()

        if not data or 'to' not in data:
            return jsonify({'error': 'Missing required field: to'}), 400

        task = Task.get_by_id(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404

        client = WhatsAppClient()
        actions = generate_quick_actions(task_id)

        result = client.send_task_notification(
            to_number=data['to'],
            task=task.to_dict(),
            action_urls=actions
        )

        return jsonify({
            'success': True,
            'message': 'Task notification sent',
            'details': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
