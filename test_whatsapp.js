/**
 * Test script to verify WhatsApp connection and send a test message
 */

const { Client, LocalAuth } = require('whatsapp-web.js');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('ready', async () => {
    console.log('✅ WhatsApp client is ready!');

    try {
        // Get the Task Manager group
        const chats = await client.getChats();
        const taskManagerGroup = chats.find(chat => chat.isGroup && chat.name === 'Task Manager');

        if (!taskManagerGroup) {
            console.log('❌ Could not find "Task Manager" group');
            process.exit(1);
        }

        console.log(`✅ Found group: ${taskManagerGroup.name}`);
        console.log(`   ID: ${taskManagerGroup.id._serialized}`);

        // Send a test message
        console.log('\n📤 Sending test message...');
        await taskManagerGroup.sendMessage('🤖 Test message from bot - if you see this, the bot is working!');
        console.log('✅ Message sent successfully!');

        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
});

client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
    process.exit(1);
});

console.log('🚀 Initializing WhatsApp client...');
client.initialize();
