/**
 * WhatsApp Task Manager Bot
 *
 * Monitors a WhatsApp group for task commands and integrates with Flask backend
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

// Configuration
const CONFIG = {
    FLASK_API_URL: process.env.FLASK_API_URL || 'http://localhost:5001',
    GROUP_NAME: process.env.WHATSAPP_GROUP_NAME || 'Task Manager', // Configure this!
    BASE_URL: process.env.BASE_URL || 'http://localhost:5001'
};

// Initialize WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// IMPORTANT: Also listen for messages from yourself (for testing)
client.on('message_create', async (message) => {
    // Trigger the same handler as regular messages
    client.emit('message', message);
});

// QR Code for authentication
client.on('qr', (qr) => {
    console.log('\n🔐 Scan this QR code with WhatsApp on your phone:\n');
    qrcode.generate(qr, { small: true });
    console.log('\nWaiting for authentication...');
});

// Client ready
client.on('ready', async () => {
    console.log('✅ WhatsApp bot is ready!');
    console.log(`📱 Monitoring group: "${CONFIG.GROUP_NAME}"`);
    console.log(`🔗 Flask API: ${CONFIG.FLASK_API_URL}`);

    // List all chats to help debug
    try {
        const chats = await client.getChats();
        console.log(`\n📋 Found ${chats.length} total chats`);
        console.log('🔍 Available groups:');
        chats
            .filter(chat => chat.isGroup)
            .forEach(chat => {
                console.log(`   - "${chat.name}" (${chat.id._serialized})`);
            });
    } catch (error) {
        console.error('Error listing chats:', error);
    }

    console.log('\nListening for commands...\n');
});

// Handle authentication failure
client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
});

// Handle disconnection
client.on('disconnected', (reason) => {
    console.log('⚠️  Client was disconnected:', reason);
});

// Parse task from WhatsApp message
function parseTaskMessage(messageBody) {
    if (!messageBody.includes('#task')) {
        return null;
    }

    const lines = messageBody.split('\n');
    const taskData = {};

    for (const line of lines) {
        const trimmed = line.trim();

        if (trimmed.startsWith('#task')) {
            continue;
        }

        if (trimmed.includes(':')) {
            const [key, ...valueParts] = trimmed.split(':');
            const value = valueParts.join(':').trim();
            const normalizedKey = key.trim().toLowerCase();

            if (normalizedKey === 'title') {
                taskData.title = value;
            } else if (normalizedKey === 'owner') {
                taskData.owner = value;
            } else if (normalizedKey === 'due') {
                taskData.due_date = value;
            } else if (normalizedKey === 'next') {
                taskData.next_step = value;
            } else if (normalizedKey === 'priority') {
                taskData.priority = value.toLowerCase();
            } else if (normalizedKey === 'category') {
                taskData.category = value.toLowerCase();
            } else if (normalizedKey === 'notes') {
                taskData.notes = value;
            }
        }
    }

    return taskData.title && taskData.owner ? taskData : null;
}

// Create task via API
async function createTask(taskData) {
    try {
        const response = await axios.post(`${CONFIG.FLASK_API_URL}/api/newTask`, taskData);
        return response.data;
    } catch (error) {
        console.error('Error creating task:', error.message);
        throw error;
    }
}

// Get all open tasks
async function getOpenTasks() {
    try {
        const response = await axios.get(`${CONFIG.FLASK_API_URL}/api/tasks?status=open`);
        return response.data.tasks;
    } catch (error) {
        console.error('Error fetching tasks:', error.message);
        throw error;
    }
}

// Get tasks by owner
async function getTasksByOwner(owner) {
    try {
        const response = await axios.get(`${CONFIG.FLASK_API_URL}/api/tasks?owner=${encodeURIComponent(owner)}`);
        return response.data.tasks;
    } catch (error) {
        console.error('Error fetching tasks:', error.message);
        throw error;
    }
}

// Format task for WhatsApp
function formatTask(task) {
    let text = `*Task #${task.id}*\n`;
    text += `📋 ${task.title}\n`;
    text += `👤 Owner: ${task.owner}\n`;

    // Priority indicator
    const priorityEmoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    };
    if (task.priority) {
        text += `${priorityEmoji[task.priority] || '⚪'} Priority: ${task.priority}\n`;
    }

    if (task.category) {
        text += `🏷️ Category: ${task.category}\n`;
    }
    if (task.due_date) {
        text += `⏰ Due: ${task.due_date}\n`;
    }
    if (task.next_step) {
        text += `➡️ Next: ${task.next_step}\n`;
    }
    return text;
}

// Format quick actions for a task
function formatQuickActions(taskId) {
    const base = CONFIG.BASE_URL;
    return `\n*Quick Actions:*
✅ Mark Done: ${base}/markDone/${taskId}
👥 Reassign to Ofek: ${base}/reassign/${taskId}?to=Ofek
👥 Reassign to Shachar: ${base}/reassign/${taskId}?to=Shachar
🔗 View: ${base}/task/${taskId}`;
}

// Message counter for debugging
let messageCount = 0;

// Handle incoming messages
client.on('message', async (message) => {
    messageCount++;
    console.log(`\n🔔 MESSAGE EVENT FIRED! Count: ${messageCount}`);

    try {
        // Only process group messages
        const chat = await message.getChat();

        console.log(`\n🔍 DEBUG: Received message - isGroup: ${chat.isGroup}, chatName: "${chat.name}"`);

        if (!chat.isGroup) {
            console.log('⏭️  Skipping: Not a group message');
            return;
        }

        // Only process messages from the configured group
        if (chat.name !== CONFIG.GROUP_NAME) {
            console.log(`⏭️  Skipping: Group "${chat.name}" != configured "${CONFIG.GROUP_NAME}"`);
            return;
        }

        const messageBody = message.body.trim();
        console.log(`\n📨 Message in ${chat.name}: ${messageBody.substring(0, 50)}...`);

        // Command: Create task
        if (messageBody.includes('#task')) {
            const taskData = parseTaskMessage(messageBody);

            if (!taskData) {
                await message.reply('❌ Could not parse task. Please use format:\n#task\nTitle: Your title\nOwner: Name\nDue: Date (optional)\nNext: Next step (optional)');
                return;
            }

            console.log('Creating task:', taskData);
            const result = await createTask(taskData);

            const reply = `✅ *Task #${result.task_id} Created!*\n\n` +
                         `📋 ${taskData.title}\n` +
                         `👤 ${taskData.owner}\n` +
                         formatQuickActions(result.task_id);

            await message.reply(reply);
            console.log(`✅ Task #${result.task_id} created`);
        }

        // Command: List all open tasks
        else if (messageBody.toLowerCase() === '#tasks' || messageBody.toLowerCase() === '#list') {
            console.log('Fetching all open tasks...');
            const tasks = await getOpenTasks();

            if (tasks.length === 0) {
                await message.reply('✅ No open tasks!');
                return;
            }

            let reply = `*📋 Open Tasks (${tasks.length})*\n\n`;
            tasks.forEach(task => {
                reply += formatTask(task) + '\n';
            });
            reply += `\nView all: ${CONFIG.BASE_URL}/open`;

            await message.reply(reply);
            console.log(`📋 Listed ${tasks.length} tasks`);
        }

        // Command: List my tasks
        else if (messageBody.toLowerCase().startsWith('#my') || messageBody.toLowerCase().startsWith('#mine')) {
            // Try to extract owner from message or use contact name
            const contact = await message.getContact();
            const owner = messageBody.split(' ')[1] || contact.pushname || 'Ofek';

            console.log(`Fetching tasks for ${owner}...`);
            const tasks = await getTasksByOwner(owner);

            if (tasks.length === 0) {
                await message.reply(`✅ No open tasks for ${owner}!`);
                return;
            }

            let reply = `*📋 ${owner}'s Tasks (${tasks.length})*\n\n`;
            tasks.forEach(task => {
                reply += formatTask(task) + '\n';
            });
            reply += `\nView: ${CONFIG.BASE_URL}/mine?owner=${encodeURIComponent(owner)}`;

            await message.reply(reply);
            console.log(`📋 Listed ${tasks.length} tasks for ${owner}`);
        }

        // Command: Help
        else if (messageBody.toLowerCase() === '#help' || messageBody === '#?') {
            const helpText = `*🤖 Task Manager Bot Commands*\n\n` +
                           `*Create Task:*\n` +
                           `#task\n` +
                           `Title: Your task title\n` +
                           `Owner: Ofek\n` +
                           `Priority: high|medium|low (optional)\n` +
                           `Category: work|home|shopping (optional)\n` +
                           `Due: Tomorrow 5pm (optional)\n` +
                           `Next: Next action (optional)\n\n` +
                           `*Priority Levels:*\n` +
                           `🔴 high - Urgent, important\n` +
                           `🟡 medium - Normal (default)\n` +
                           `🟢 low - Can wait\n\n` +
                           `*List Tasks:*\n` +
                           `#tasks or #list - All open tasks\n` +
                           `#my or #mine - Your tasks\n` +
                           `#my Shachar - Shachar's tasks\n\n` +
                           `*Quick Actions:*\n` +
                           `Tap links in task messages to mark done or reassign\n\n` +
                           `*Help:*\n` +
                           `#help or #? - Show this help`;

            await message.reply(helpText);
            console.log('📖 Sent help message');
        }

    } catch (error) {
        console.error('Error handling message:', error);
        try {
            await message.reply(`❌ Error: ${error.message}`);
        } catch (replyError) {
            console.error('Could not send error reply:', replyError);
        }
    }
});

// Error handler
client.on('error', (error) => {
    console.error('WhatsApp client error:', error);
});

// Start the client
console.log('🚀 Starting WhatsApp Task Manager Bot...\n');
client.initialize();
