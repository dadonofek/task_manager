/**
 * Basic Usage Example
 * Shows the three core methods: start(), listen(), and send()
 */

const WhatsAppBot = require('../index');

// Create a new bot instance
const bot = new WhatsAppBot({
    groupName: 'My Group', // Optional: only listen to this group
    logQR: true            // Optional: show QR code in terminal (default: true)
});

// Main function
async function main() {
    try {
        console.log('Starting WhatsApp bot...');

        // 1. Start the bot (handles QR code authentication)
        await bot.start();

        console.log('Bot is ready! Send messages to test.\n');

        // 2. Listen for incoming messages
        bot.listen((message) => {
            console.log('Received message:');
            console.log('  From:', message.from);
            console.log('  Chat:', message.chat.name);
            console.log('  Body:', message.body);
            console.log('');

            // Echo back the message
            if (message.body.toLowerCase() === 'ping') {
                message.reply('Pong! 🏓');
            }
        });

        // Example: Send a message after 5 seconds
        // Replace with actual WhatsApp ID (e.g., '1234567890@c.us')
        setTimeout(async () => {
            try {
                // 3. Send a message
                // await bot.send('1234567890@c.us', 'Hello from the bot!');
                console.log('To send a message, use: await bot.send("1234567890@c.us", "Your message")');
            } catch (error) {
                console.error('Error sending message:', error.message);
            }
        }, 5000);

    } catch (error) {
        console.error('Error starting bot:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down bot...');
    await bot.stop();
    process.exit(0);
});

// Run the bot
main();
