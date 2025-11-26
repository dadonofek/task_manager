/**
 * WhatsApp Task Manager Bot - Refactored Version
 *
 * This version uses the simple-whatsapp-bot package
 * Demonstrates how the original bot can be simplified
 */

const WhatsAppBot = require('./simple-whatsapp-bot');
const axios = require('axios');

// Configuration
const CONFIG = {
    FLASK_API_URL: process.env.FLASK_API_URL || 'http://localhost:5001',
    GROUP_NAME: process.env.WHATSAPP_GROUP_NAME || 'Task Manager',
    BASE_URL: process.env.BASE_URL || 'http://localhost:5001'
};

// Create bot instance with group filtering
const bot = new WhatsAppBot({
    groupName: CONFIG.GROUP_NAME,
    logQR: true
});

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Parse task from WhatsApp message
 */
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

/**
 * Create task via API
 */
async function createTask(taskData) {
    try {
        const response = await axios.post(`${CONFIG.FLASK_API_URL}/api/newTask`, taskData);
        return response.data;
    } catch (error) {
        console.error('Error creating task:', error.message);
        throw error;
    }
}

/**
 * Get all open tasks
 */
async function getOpenTasks() {
    try {
        const response = await axios.get(`${CONFIG.FLASK_API_URL}/api/tasks?status=open`);
        return response.data.tasks;
    } catch (error) {
        console.error('Error fetching tasks:', error.message);
        throw error;
    }
}

/**
 * Get tasks by owner
 */
async function getTasksByOwner(owner) {
    try {
        const response = await axios.get(`${CONFIG.FLASK_API_URL}/api/tasks?owner=${encodeURIComponent(owner)}`);
        return response.data.tasks;
    } catch (error) {
        console.error('Error fetching tasks:', error.message);
        throw error;
    }
}

/**
 * Format task for WhatsApp
 */
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

/**
 * Format quick actions for a task
 */
function formatQuickActions(taskId) {
    const base = CONFIG.BASE_URL;
    return `\n*Quick Actions:*
✅ Mark Done: ${base}/markDone/${taskId}
👥 Reassign to Ofek: ${base}/reassign/${taskId}?to=Ofek
👥 Reassign to Shachar: ${base}/reassign/${taskId}?to=Shachar
🔗 View: ${base}/task/${taskId}`;
}

// ============================================================================
// Main Bot Logic
// ============================================================================

async function main() {
    try {
        console.log('🚀 Starting WhatsApp Task Manager Bot...\n');

        // 1. Start the bot (handles QR code authentication)
        await bot.start();

        console.log(`📱 Monitoring group: "${CONFIG.GROUP_NAME}"`);
        console.log(`🔗 Flask API: ${CONFIG.FLASK_API_URL}`);
        console.log('\nListening for commands...\n');

        // 2. Listen for incoming messages
        bot.listen(async (message) => {
            const messageBody = message.body.trim();

            console.log(`\n📨 Message in ${message.chat.name}: ${messageBody.substring(0, 50)}...`);

            try {
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
                    // Try to extract owner from message
                    const owner = messageBody.split(' ')[1] || 'Ofek';

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

    } catch (error) {
        console.error('Error starting bot:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down...');
    await bot.stop();
    process.exit(0);
});

// Start the bot
main();
