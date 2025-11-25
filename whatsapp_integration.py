"""WhatsApp integration using Twilio Sandbox API.

This module provides functions to send and receive WhatsApp messages via Twilio.

Setup:
1. Sign up for Twilio account at https://www.twilio.com
2. Get your Account SID and Auth Token from the Twilio Console
3. Join the WhatsApp Sandbox by sending "join <keyword>" to the sandbox number
4. Configure webhook URL in Twilio Console -> WhatsApp Sandbox Settings

Environment Variables Required:
- TWILIO_ACCOUNT_SID: Your Twilio Account SID
- TWILIO_AUTH_TOKEN: Your Twilio Auth Token
- TWILIO_WHATSAPP_NUMBER: Your Twilio WhatsApp number (e.g., 'whatsapp:+14155238886')
"""

import os
from typing import Optional, Dict, List
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse


class WhatsAppClient:
    """Client for sending and receiving WhatsApp messages via Twilio."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """Initialize the WhatsApp client.

        Args:
            account_sid: Twilio Account SID (defaults to env var TWILIO_ACCOUNT_SID)
            auth_token: Twilio Auth Token (defaults to env var TWILIO_AUTH_TOKEN)
            from_number: WhatsApp number to send from (defaults to env var TWILIO_WHATSAPP_NUMBER)
        """
        self.account_sid = account_sid or os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = from_number or os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

        if not self.account_sid or not self.auth_token:
            raise ValueError(
                "Twilio credentials not found. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN "
                "environment variables or pass them to the constructor."
            )

        self.client = Client(self.account_sid, self.auth_token)

    def send_message(
        self,
        to_number: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict:
        """Send a WhatsApp message.

        Args:
            to_number: Recipient's phone number in E.164 format (e.g., '+1234567890')
                      Will be automatically prefixed with 'whatsapp:' if not present
            body: Message text
            media_url: Optional URL of media to send (image, PDF, etc.)

        Returns:
            Dict containing message details including 'sid' and 'status'

        Example:
            client = WhatsAppClient()
            result = client.send_message('+1234567890', 'Hello from Task Manager!')
        """
        # Ensure number has whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        message_params = {
            'from_': self.from_number,
            'to': to_number,
            'body': body
        }

        if media_url:
            message_params['media_url'] = [media_url]

        message = self.client.messages.create(**message_params)

        return {
            'sid': message.sid,
            'status': message.status,
            'to': message.to,
            'from': message.from_,
            'body': message.body,
            'date_created': message.date_created.isoformat() if message.date_created else None
        }

    def send_task_notification(
        self,
        to_number: str,
        task: Dict,
        action_urls: Optional[Dict] = None
    ) -> Dict:
        """Send a formatted task notification.

        Args:
            to_number: Recipient's phone number
            task: Task dictionary with title, owner, due_date, etc.
            action_urls: Optional dict with action URLs (mark_done, reassign, etc.)

        Returns:
            Dict containing message details
        """
        message = self._format_task_message(task, action_urls)
        return self.send_message(to_number, message)

    def send_task_list(
        self,
        to_number: str,
        tasks: List[Dict],
        title: str = "Your Tasks"
    ) -> Dict:
        """Send a formatted list of tasks.

        Args:
            to_number: Recipient's phone number
            tasks: List of task dictionaries
            title: Title for the task list

        Returns:
            Dict containing message details
        """
        message = f"*{title}*\n\n"

        if not tasks:
            message += "No tasks found."
        else:
            for i, task in enumerate(tasks, 1):
                message += f"{i}. {task['title']}\n"
                message += f"   Owner: {task['owner']}\n"
                if task.get('due_date'):
                    message += f"   Due: {task['due_date']}\n"
                if task.get('next_step'):
                    message += f"   Next: {task['next_step']}\n"
                message += "\n"

        return self.send_message(to_number, message)

    @staticmethod
    def _format_task_message(task: Dict, action_urls: Optional[Dict] = None) -> str:
        """Format a task as a WhatsApp message.

        Args:
            task: Task dictionary
            action_urls: Optional dict with action URLs

        Returns:
            Formatted message string
        """
        message = f"*Task #{task['id']}: {task['title']}*\n\n"
        message += f"Owner: {task['owner']}\n"

        if task.get('due_date'):
            message += f"Due: {task['due_date']}\n"

        if task.get('next_step'):
            message += f"Next step: {task['next_step']}\n"

        if task.get('status'):
            message += f"Status: {task['status']}\n"

        if task.get('notes'):
            message += f"\nNotes: {task['notes']}\n"

        if action_urls:
            message += "\n*Quick Actions:*\n"
            if 'mark_done' in action_urls:
                message += f"✓ Mark Done: {action_urls['mark_done']}\n"
            if 'view_task' in action_urls:
                message += f"👁 View: {action_urls['view_task']}\n"

        return message

    @staticmethod
    def parse_incoming_message(request_data: Dict) -> Dict:
        """Parse incoming webhook data from Twilio.

        Args:
            request_data: Form data from Twilio webhook request

        Returns:
            Dict with parsed message data including:
                - from_number: Sender's WhatsApp number
                - to_number: Recipient's WhatsApp number (your number)
                - body: Message text
                - num_media: Number of media attachments
                - media_urls: List of media URLs (if any)
        """
        media_urls = []
        num_media = int(request_data.get('NumMedia', 0))

        for i in range(num_media):
            media_url = request_data.get(f'MediaUrl{i}')
            if media_url:
                media_urls.append(media_url)

        return {
            'from_number': request_data.get('From', ''),
            'to_number': request_data.get('To', ''),
            'body': request_data.get('Body', '').strip(),
            'num_media': num_media,
            'media_urls': media_urls,
            'message_sid': request_data.get('MessageSid', '')
        }

    @staticmethod
    def create_response(message: str) -> str:
        """Create a TwiML response for replying to incoming messages.

        Args:
            message: Reply message text

        Returns:
            TwiML XML string

        Example:
            response = WhatsAppClient.create_response('Thanks for your message!')
            return response, 200, {'Content-Type': 'text/xml'}
        """
        resp = MessagingResponse()
        resp.message(message)
        return str(resp)


# Convenience functions for quick usage

def send_whatsapp_message(to_number: str, body: str, media_url: Optional[str] = None) -> Dict:
    """Send a WhatsApp message (convenience function).

    Args:
        to_number: Recipient's phone number
        body: Message text
        media_url: Optional media URL

    Returns:
        Dict containing message details
    """
    client = WhatsAppClient()
    return client.send_message(to_number, body, media_url)


def send_task_update(to_number: str, task: Dict, action_urls: Optional[Dict] = None) -> Dict:
    """Send a task notification (convenience function).

    Args:
        to_number: Recipient's phone number
        task: Task dictionary
        action_urls: Optional action URLs

    Returns:
        Dict containing message details
    """
    client = WhatsAppClient()
    return client.send_task_notification(to_number, task, action_urls)
