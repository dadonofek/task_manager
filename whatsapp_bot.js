/**
 * WhatsApp Task Manager Bot
 *
 * Monitors a dedicated WhatsApp group for task messages and automatically
 * creates tasks via the backend API.
 *
 * ⚠️ WARNING: This uses whatsapp-web.js which is unofficial and may result
 * in account suspension. Use at your own risk!
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');
require('dotenv').config();

// Configuration
const CONFIG = {
    mode: process.env.WHATSAPP_MODE || 'manual',
    backendUrl: process.env.BACKEND_URL || 'http://localhost:5000',
    groupName: process.env.WHATSAPP_GROUP_NAME || 'My Tasks',
    chatName: process.env.WHATSAPP_CHAT_NAME || '',
    autoReply: process.env.AUTO_REPLY_ENABLED !== 'false',
    maxTasksPerHour: parseInt(process.env.MAX_TASKS_PER_HOUR) || 20,
    quietHours: process.env.QUIET_HOURS || '23-07',
    saveSession: process.env.SAVE_SESSION !== 'false',
    logLevel: process.env.LOG_LEVEL || 'info'
};

// Rate limiting tracker
const taskCounter = {
    count: 0,
    resetTime: Date.now() + 3600000 // 1 hour from now
};

// Logging utility
const log = {
    debug: (...args) => CONFIG.logLevel === 'debug' && console.log('[DEBUG]', ...args),
    info: (...args) => ['debug', 'info'].includes(CONFIG.logLevel) && console.log('[INFO]', ...args),
    warn: (...args) => console.warn('[WARN]', ...args),
    error: (...args) => console.error('[ERROR]', ...args)
};

// Check if we're in quiet hours
function isQuietHours() {
    const [startHour, endHour] = CONFIG.quietHours.split('-').map(Number);
    const currentHour = new Date().getHours();

    if (startHour > endHour) {
        // Spans midnight (e.g., 23-07)
        return currentHour >= startHour || currentHour < endHour;
    } else {
        // Same day (e.g., 01-06)
        return currentHour >= startHour && currentHour < endHour;
    }
}

// Check rate limit
function checkRateLimit() {
    const now = Date.now();

    // Reset counter if hour has passed
    if (now >= taskCounter.resetTime) {
        taskCounter.count = 0;
        taskCounter.resetTime = now + 3600000;
    }

    if (taskCounter.count >= CONFIG.maxTasksPerHour) {
        log.warn('Rate limit reached. Ignoring task.');
        return false;
    }

    taskCounter.count++;
    return true;
}

// Parse task message in WhatsApp format
function parseTaskMessage(messageBody) {
    log.debug('Parsing message:', messageBody);

    // Check if message starts with #task
    if (!messageBody.trim().startsWith('#task')) {
        return null;
    }

    const lines = messageBody.split('\n');
    const task = {};

    for (const line of lines) {
        const titleMatch = line.match(/^Title:\s*(.+)$/i);
        const ownerMatch = line.match(/^Owner:\s*(.+)$/i);
        const dueMatch = line.match(/^Due:\s*(.+)$/i);
        const nextMatch = line.match(/^Next:\s*(.+)$/i);
        const notesMatch = line.match(/^Notes:\s*(.+)$/i);

        if (titleMatch) task.title = titleMatch[1].trim();
        if (ownerMatch) task.owner = ownerMatch[1].trim();
        if (dueMatch) task.due_date = dueMatch[1].trim();
        if (nextMatch) task.next_step = nextMatch[1].trim();
        if (notesMatch) task.notes = notesMatch[1].trim();
    }

    // Title and owner are required
    if (!task.title || !task.owner) {
        log.warn('Invalid task format: missing title or owner');
        return null;
    }

    log.info('Parsed task:', task);
    return task;
}

// Create task via backend API
async function createTask(taskData) {
    try {
        log.info('Creating task via backend API...');
        const response = await axios.post(`${CONFIG.backendUrl}/api/newTask`, taskData, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 10000
        });

        if (response.data.success) {
            log.info(`Task created successfully! ID: ${response.data.task_id}`);
            return response.data;
        } else {
            log.error('Backend returned error:', response.data.message);
            return null;
        }
    } catch (error) {
        log.error('Failed to create task:', error.message);
        return null;
    }
}

// Format reply message with quick actions
function formatReplyMessage(taskResult) {
    const { task_id, task, quick_actions } = taskResult;

    let reply = `✅ *Task #${task_id} Created!*\n\n`;
    reply += `📋 *${task.title}*\n`;
    reply += `👤 Owner: ${task.owner}\n`;

    if (task.due_date) {
        reply += `⏰ Due: ${task.due_date}\n`;
    }

    if (task.next_step) {
        reply += `➡️ Next: ${task.next_step}\n`;
    }

    reply += `\n🔗 *Quick Actions:*\n`;
    reply += `View: ${quick_actions.view}\n`;
    reply += `Done: ${quick_actions.mark_done}\n`;

    if (quick_actions.reassign) {
        reply += `\n_Reassign:_\n`;
        for (const [owner, url] of Object.entries(quick_actions.reassign)) {
            reply += `→ ${owner}: ${url}\n`;
        }
    }

    return reply;
}

// Main message handler
async function handleMessage(message) {
    try {
        const chat = await message.getChat();
        const contact = await message.getContact();
        const chatName = chat.name || contact.pushname || contact.number;

        log.debug(`Message from: ${chatName}`);
        log.debug(`Chat type: ${chat.isGroup ? 'Group' : 'Individual'}`);

        // Check if message is from the configured group or chat
        const isTargetChat =
            (chat.isGroup && chat.name === CONFIG.groupName) ||
            (!chat.isGroup && chatName === CONFIG.chatName) ||
            (!CONFIG.groupName && !CONFIG.chatName); // Monitor all if not configured

        if (!isTargetChat) {
            log.debug(`Ignoring message from: ${chatName}`);
            return;
        }

        // Check quiet hours
        if (isQuietHours()) {
            log.info('In quiet hours. Ignoring message.');
            return;
        }

        // Check rate limit
        if (!checkRateLimit()) {
            await message.reply('⚠️ Rate limit reached. Please try again later.');
            return;
        }

        // Parse task message
        const taskData = parseTaskMessage(message.body);
        if (!taskData) {
            log.debug('Not a task message, ignoring.');
            return;
        }

        log.info(`Processing task: ${taskData.title}`);

        // Create task via backend
        const result = await createTask(taskData);

        if (!result) {
            await message.reply('❌ Failed to create task. Please check the backend server.');
            return;
        }

        // Send confirmation reply
        if (CONFIG.autoReply) {
            const replyText = formatReplyMessage(result);
            await message.reply(replyText);
            log.info('Sent confirmation reply');
        }

    } catch (error) {
        log.error('Error handling message:', error);
    }
}

// Initialize WhatsApp client
function initializeClient() {
    log.info('Initializing WhatsApp client...');
    log.warn('⚠️  WARNING: Using whatsapp-web.js may result in account ban!');
    log.info(`Mode: ${CONFIG.mode}`);
    log.info(`Monitoring group: ${CONFIG.groupName || 'All chats'}`);

    if (CONFIG.mode !== 'automated') {
        log.info('WhatsApp mode is not "automated". Exiting...');
        log.info('To enable automation, set WHATSAPP_MODE=automated in .env file');
        process.exit(0);
    }

    const clientOptions = {
        puppeteer: {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        }
    };

    // Enable session persistence
    if (CONFIG.saveSession) {
        clientOptions.authStrategy = new LocalAuth({
            dataPath: './.wwebjs_auth'
        });
        log.info('Session persistence enabled');
    }

    const client = new Client(clientOptions);

    // QR code event
    client.on('qr', (qr) => {
        log.info('📱 Scan this QR code with WhatsApp:');
        qrcode.generate(qr, { small: true });
        log.info('\nOpen WhatsApp > Settings > Linked Devices > Link a Device');
    });

    // Ready event
    client.on('ready', () => {
        log.info('✅ WhatsApp client is ready!');
        log.info(`Monitoring: ${CONFIG.groupName || 'All chats'}`);
        log.info('Send a message with #task format to create tasks automatically');
    });

    // Authenticated event
    client.on('authenticated', () => {
        log.info('✅ Authenticated successfully!');
    });

    // Auth failure event
    client.on('auth_failure', (msg) => {
        log.error('❌ Authentication failed:', msg);
        log.error('Please delete ./.wwebjs_auth folder and try again');
    });

    // Disconnected event
    client.on('disconnected', (reason) => {
        log.warn('❌ Client disconnected:', reason);
        log.warn('Attempting to reconnect...');
    });

    // Message event
    client.on('message', handleMessage);

    // Initialize the client
    client.initialize();

    return client;
}

// Graceful shutdown
function setupGracefulShutdown(client) {
    const shutdown = async () => {
        log.info('Shutting down gracefully...');
        try {
            await client.destroy();
            log.info('Client destroyed successfully');
            process.exit(0);
        } catch (error) {
            log.error('Error during shutdown:', error);
            process.exit(1);
        }
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
}

// Main entry point
if (require.main === module) {
    log.info('='.repeat(50));
    log.info('WhatsApp Task Manager Bot');
    log.info('='.repeat(50));

    const client = initializeClient();
    setupGracefulShutdown(client);
}

module.exports = { initializeClient, parseTaskMessage, createTask };
