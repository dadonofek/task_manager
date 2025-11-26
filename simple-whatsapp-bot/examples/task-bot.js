/**
 * Task Bot Example
 * Shows how to build a simple task management bot
 */

const WhatsAppBot = require('../index');
const axios = require('axios');

// Configuration
const CONFIG = {
    FLASK_API_URL: process.env.FLASK_API_URL || 'http://localhost:5001',
    GROUP_NAME: process.env.WHATSAPP_GROUP_NAME || 'Task Manager'
};

// Create bot instance
const bot = new WhatsAppBot({
    groupName: CONFIG.GROUP_NAME,
    logQR: true
});

// Parse task from message
function parseTaskMessage(messageBody) {
    if (!messageBody.includes('#task')) {
        return null;
    }

    const lines = messageBody.split('\n');
    const taskData = {};

    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('#task')) continue;

        if (trimmed.includes(':')) {
            const [key, ...valueParts] = trimmed.split(':');
            const value = valueParts.join(':').trim();
            const normalizedKey = key.trim().toLowerCase();

            if (normalizedKey === 'title') taskData.title = value;
            else if (normalizedKey === 'owner') taskData.owner = value;
            else if (normalizedKey === 'due') taskData.due_date = value;
            else if (normalizedKey === 'priority') taskData.priority = value.toLowerCase();
            else if (normalizedKey === 'category') taskData.category = value.toLowerCase();
        }
    }

    return taskData.title && taskData.owner ? taskData : null;
}

// Create task via API
async function createTask(taskData) {
    const response = await axios.post(`${CONFIG.FLASK_API_URL}/api/newTask`, taskData);
    return response.data;
}

// Main function
async function main() {
    try {
        console.log('Starting Task Manager bot...\n');

        // Start the bot
        await bot.start();

        console.log(`Monitoring group: "${CONFIG.GROUP_NAME}"`);
        console.log(`Flask API: ${CONFIG.FLASK_API_URL}\n`);

        // Listen for messages
        bot.listen(async (message) => {
            const body = message.body.trim();

            // Command: Create task
            if (body.includes('#task')) {
                const taskData = parseTaskMessage(body);

                if (!taskData) {
                    await message.reply('❌ Could not parse task. Please use format:\n#task\nTitle: Your title\nOwner: Name');
                    return;
                }

                try {
                    const result = await createTask(taskData);
                    const reply = `✅ *Task #${result.task_id} Created!*\n\n` +
                                `📋 ${taskData.title}\n` +
                                `👤 ${taskData.owner}\n\n` +
                                `🔗 View: ${CONFIG.FLASK_API_URL}/task/${result.task_id}`;

                    await message.reply(reply);
                    console.log(`✅ Task #${result.task_id} created`);
                } catch (error) {
                    await message.reply(`❌ Error creating task: ${error.message}`);
                }
            }

            // Command: Help
            else if (body.toLowerCase() === '#help') {
                const helpText = `*🤖 Task Manager Bot*\n\n` +
                               `*Create Task:*\n` +
                               `#task\n` +
                               `Title: Your task title\n` +
                               `Owner: Your name\n` +
                               `Priority: high|medium|low (optional)\n` +
                               `Category: work|home (optional)\n` +
                               `Due: Tomorrow 5pm (optional)`;

                await message.reply(helpText);
            }
        });

    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

// Handle shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await bot.stop();
    process.exit(0);
});

// Run
main();
