# Simple WhatsApp Bot

A minimal, production-ready WhatsApp bot package with a clean API. Build WhatsApp bots with just 3 methods: `start()`, `listen()`, and `send()`.

## ✨ Features

- **🚀 Simple API** - Just 3 core methods to learn
- **📱 Real WhatsApp Integration** - Uses WhatsApp Web protocol (no unofficial APIs)
- **🔐 QR Code Authentication** - Secure authentication via QR code scanning
- **💾 Persistent Sessions** - Authentication persists across restarts
- **🎯 Group Filtering** - Optional: Listen only to specific groups
- **⚡ Production Ready** - Built on battle-tested `whatsapp-web.js`
- **🔧 Minimal Dependencies** - Only 2 core dependencies

## 📦 Installation

```bash
npm install simple-whatsapp-bot
```

Or install from source:

```bash
git clone https://github.com/yourusername/simple-whatsapp-bot.git
cd simple-whatsapp-bot
npm install
```

## 🚀 Quick Start

```javascript
const WhatsAppBot = require('simple-whatsapp-bot');

const bot = new WhatsAppBot();

async function main() {
    // 1. Start the bot
    await bot.start(); // Shows QR code - scan with WhatsApp

    // 2. Listen for messages
    bot.listen((message) => {
        console.log('From:', message.from);
        console.log('Message:', message.body);

        // Reply to the message
        if (message.body === 'ping') {
            message.reply('pong! 🏓');
        }
    });

    // 3. Send messages
    await bot.send('1234567890@c.us', 'Hello from bot!');
}

main();
```

## 📖 Core API

### Constructor Options

```javascript
const bot = new WhatsAppBot({
    groupName: 'My Group',        // Optional: Only listen to this group
    authPath: './.auth',          // Optional: Custom auth storage path
    logQR: true,                  // Optional: Show QR code in terminal (default: true)
    puppeteerOptions: {}          // Optional: Custom Puppeteer config
});
```

### Methods

#### `start()` - Initialize and Start the Bot

```javascript
await bot.start();
```

- Shows QR code for authentication (first time only)
- Authenticates with WhatsApp Web
- Returns a Promise that resolves when bot is ready
- Throws error if authentication fails

**First Run:**
1. QR code appears in terminal
2. Open WhatsApp on your phone
3. Go to Settings → Linked Devices → Link a Device
4. Scan the QR code
5. Bot is now authenticated!

**Subsequent Runs:**
- No QR code needed - uses saved session
- Bot starts immediately

---

#### `listen(callback)` - Listen for Incoming Messages

```javascript
bot.listen((message) => {
    // Handle incoming message
});
```

**Message Object Properties:**

```javascript
{
    from: '1234567890@c.us',           // Sender's WhatsApp ID
    to: '0987654321@c.us',             // Recipient's WhatsApp ID
    body: 'Hello!',                     // Message text
    timestamp: 1234567890,              // Unix timestamp
    chat: {
        id: 'xxxxx@g.us',              // Chat ID
        name: 'My Group',              // Chat/Group name
        isGroup: true                  // true if group chat
    },
    reply: async (text) => {},         // Helper to reply to this message
    raw: MessageObject                 // Original whatsapp-web.js message object
}
```

**Example: Echo Bot**

```javascript
bot.listen((message) => {
    message.reply(`You said: ${message.body}`);
});
```

**Example: Command Bot**

```javascript
bot.listen((message) => {
    if (message.body === '/help') {
        message.reply('Available commands:\n/help - Show this message\n/ping - Test bot');
    }
    else if (message.body === '/ping') {
        message.reply('Pong! Bot is alive! 🤖');
    }
});
```

---

#### `send(to, message)` - Send a Message

```javascript
await bot.send(to, message);
```

**Parameters:**
- `to` (string): WhatsApp ID
  - Individual: `'1234567890@c.us'`
  - Group: `'xxxxx@g.us'`
- `message` (string): Text to send

**Returns:** Promise that resolves with sent message object

**Example:**

```javascript
// Send to individual
await bot.send('1234567890@c.us', 'Hello from bot!');

// Send to group
await bot.send('123456789-987654321@g.us', 'Group announcement!');
```

**How to get WhatsApp IDs:**

```javascript
// List all chats
const chats = await bot.getChats();
chats.forEach(chat => {
    console.log(`${chat.name}: ${chat.id._serialized}`);
});
```

---

### Additional Methods

#### `stop()` - Stop the Bot

```javascript
await bot.stop();
```

Disconnects and cleans up resources. Always call this before exiting your app.

---

#### `getChats()` - Get All Chats

```javascript
const chats = await bot.getChats();
console.log(chats); // Array of chat objects
```

Returns array of all chats (individuals and groups).

---

#### `getChat(chatId)` - Get Specific Chat

```javascript
const chat = await bot.getChat('1234567890@c.us');
console.log(chat.name); // Chat name
```

---

## 📚 Examples

### Example 1: Simple Echo Bot

```javascript
const WhatsAppBot = require('simple-whatsapp-bot');

const bot = new WhatsAppBot();

async function main() {
    await bot.start();

    bot.listen((message) => {
        console.log(`${message.chat.name}: ${message.body}`);
        message.reply(`Echo: ${message.body}`);
    });
}

main();
```

### Example 2: Group-Only Bot

```javascript
const bot = new WhatsAppBot({
    groupName: 'My Project Team' // Only listen to this group
});

await bot.start();

bot.listen((message) => {
    // This will only fire for messages in "My Project Team"
    console.log(`Message in team group: ${message.body}`);
});
```

### Example 3: Command Bot

```javascript
const bot = new WhatsAppBot();

await bot.start();

bot.listen(async (message) => {
    const cmd = message.body.toLowerCase();

    if (cmd === '/time') {
        await message.reply(`Current time: ${new Date().toLocaleString()}`);
    }
    else if (cmd === '/joke') {
        await message.reply('Why did the bot cross the road? To get to the other API! 🤖');
    }
    else if (cmd === '/help') {
        await message.reply('Commands:\n/time - Get current time\n/joke - Get a joke\n/help - Show this');
    }
});
```

### Example 4: Task Manager Bot

```javascript
const WhatsAppBot = require('simple-whatsapp-bot');
const axios = require('axios');

const bot = new WhatsAppBot({
    groupName: 'Task Manager'
});

await bot.start();

bot.listen(async (message) => {
    if (message.body.startsWith('#task')) {
        // Parse task from message
        const lines = message.body.split('\n');
        const taskData = {};

        lines.forEach(line => {
            if (line.includes(':')) {
                const [key, value] = line.split(':');
                taskData[key.trim().toLowerCase()] = value.trim();
            }
        });

        // Create task via API
        const response = await axios.post('http://localhost:5001/api/newTask', {
            title: taskData.title,
            owner: taskData.owner
        });

        await message.reply(`✅ Task #${response.data.task_id} created!`);
    }
});
```

### Example 5: Scheduled Messages

```javascript
const bot = new WhatsAppBot();

await bot.start();

// Send a daily reminder at 9 AM
setInterval(async () => {
    const now = new Date();
    if (now.getHours() === 9 && now.getMinutes() === 0) {
        await bot.send('GROUP_ID@g.us', '☀️ Good morning! Daily standup in 30 minutes.');
    }
}, 60000); // Check every minute
```

## 🎯 Use Cases

- **Task Management Bots** - Create, assign, and track tasks via WhatsApp
- **Notification Systems** - Send automated alerts and reminders
- **Customer Support** - Auto-respond to common questions
- **Team Coordination** - Manage team communication and workflows
- **IoT Integration** - Control smart devices via WhatsApp messages
- **Data Collection** - Gather information through conversational forms
- **Webhook Receivers** - Trigger WhatsApp messages from external events

## 🔧 Advanced Configuration

### Custom Puppeteer Options

```javascript
const bot = new WhatsAppBot({
    puppeteerOptions: {
        executablePath: '/path/to/chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});
```

### Custom Authentication Path

```javascript
const bot = new WhatsAppBot({
    authPath: './my-custom-auth-folder'
});
```

This is useful when running multiple bots with different WhatsApp accounts.

### Event Listeners

```javascript
bot.on('qr', (qr) => {
    console.log('QR Code received:', qr);
});

bot.on('ready', () => {
    console.log('Bot is ready!');
});

bot.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
});

bot.on('disconnected', (reason) => {
    console.log('Bot disconnected:', reason);
});

bot.on('error', (error) => {
    console.error('Bot error:', error);
});
```

## 🛠️ Troubleshooting

### QR Code Won't Scan

- Make sure your terminal window is large enough
- Try zooming out if QR code is too large
- Ensure good lighting when scanning
- Use WhatsApp on your phone (not desktop/web)

### Authentication Fails

```bash
# Remove saved session and try again
rm -rf .wwebjs_auth
```

Then restart your bot.

### Bot Not Receiving Messages

- Check that `groupName` matches exactly (case-sensitive)
- Ensure bot is properly authenticated
- Check that Flask backend (if using) is running
- Look for errors in console output

### Port Already in Use (macOS)

If using port 5001 and getting conflicts:
```
System Settings → General → AirDrop & Handoff → Disable AirPlay Receiver
```

### Chrome/Chromium Not Found

Specify Chrome path manually:

```javascript
const bot = new WhatsAppBot({
    puppeteerOptions: {
        executablePath: '/path/to/chrome'
    }
});
```

Common paths:
- macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Linux: `/usr/bin/google-chrome` or `/usr/bin/chromium-browser`
- Windows: `C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe`

## 📦 Dependencies

This package uses:
- **whatsapp-web.js** (^1.25.0) - WhatsApp Web API wrapper
- **qrcode-terminal** (^0.12.0) - QR code display in terminal

## 🔐 Security Considerations

- **Authentication Data**: `.wwebjs_auth` folder contains sensitive session data. Add to `.gitignore`
- **Environment Variables**: Store API URLs and sensitive config in `.env` files
- **Rate Limiting**: WhatsApp may ban accounts that send too many messages. Implement delays.
- **Input Validation**: Always validate and sanitize message content
- **HTTPS**: Use HTTPS for API calls to backend services

## 📄 License

MIT License - Free to use in personal and commercial projects.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 💡 Tips

1. **Test Thoroughly**: Test with a test WhatsApp account first
2. **Handle Errors**: Always wrap API calls in try-catch blocks
3. **Graceful Shutdown**: Always call `bot.stop()` before exiting
4. **Monitor Logs**: Keep an eye on console output for debugging
5. **Backup Auth**: Back up `.wwebjs_auth` to avoid re-authenticating

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Check existing issues or create a new one
- **Documentation**: See examples folder for more code samples

## 🎉 Success Stories

Share how you're using simple-whatsapp-bot! Open an issue with the tag `showcase`.

---

**Built with ❤️ for developers who need simple, reliable WhatsApp automation**
