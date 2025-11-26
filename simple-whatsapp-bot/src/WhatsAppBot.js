/**
 * Simple WhatsApp Bot
 * A minimal, reusable WhatsApp bot with clean API
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

class WhatsAppBot {
    /**
     * Create a new WhatsApp Bot
     * @param {Object} options - Configuration options
     * @param {string} options.groupName - Optional: Filter messages by group name
     * @param {string} options.authPath - Optional: Custom authentication storage path (default: .wwebjs_auth)
     * @param {boolean} options.logQR - Optional: Display QR code in terminal (default: true)
     * @param {Object} options.puppeteerOptions - Optional: Custom Puppeteer options
     */
    constructor(options = {}) {
        this.options = {
            groupName: options.groupName || null,
            authPath: options.authPath || '.wwebjs_auth',
            logQR: options.logQR !== false,
            puppeteerOptions: options.puppeteerOptions || {}
        };

        this.client = null;
        this.messageHandlers = [];
        this.isReady = false;
        this.isStarting = false;
    }

    /**
     * Start the WhatsApp bot
     * @returns {Promise<void>}
     */
    async start() {
        if (this.isStarting || this.isReady) {
            throw new Error('Bot is already started or starting');
        }

        this.isStarting = true;

        return new Promise((resolve, reject) => {
            // Initialize WhatsApp client
            const clientOptions = {
                authStrategy: new LocalAuth({
                    dataPath: this.options.authPath
                }),
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
                    ],
                    ...this.options.puppeteerOptions
                }
            };

            // Try to detect Chrome installation
            const possibleChromePaths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', // macOS
                '/usr/bin/google-chrome', // Linux
                '/usr/bin/chromium-browser', // Linux alternative
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', // Windows
                'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' // Windows 32-bit
            ];

            // Only set executablePath if provided in options
            if (this.options.puppeteerOptions.executablePath) {
                clientOptions.puppeteer.executablePath = this.options.puppeteerOptions.executablePath;
            }

            this.client = new Client(clientOptions);

            // QR Code for authentication
            this.client.on('qr', (qr) => {
                if (this.options.logQR) {
                    console.log('\n🔐 Scan this QR code with WhatsApp:\n');
                    qrcode.generate(qr, { small: true });
                    console.log('\nWaiting for authentication...\n');
                }
                this.emit('qr', qr);
            });

            // Client ready
            this.client.on('ready', async () => {
                this.isReady = true;
                this.isStarting = false;
                this.emit('ready');

                if (this.options.logQR) {
                    console.log('✅ WhatsApp bot is ready!\n');
                }

                resolve();
            });

            // Authentication failure
            this.client.on('auth_failure', (msg) => {
                this.isStarting = false;
                this.emit('auth_failure', msg);
                reject(new Error(`Authentication failed: ${msg}`));
            });

            // Disconnection
            this.client.on('disconnected', (reason) => {
                this.isReady = false;
                this.emit('disconnected', reason);
            });

            // Handle incoming messages
            this.client.on('message', async (message) => {
                await this._handleMessage(message);
            });

            // Also listen for messages from yourself (important for testing)
            this.client.on('message_create', async (message) => {
                // Forward to the same handler
                this.client.emit('message', message);
            });

            // Error handler
            this.client.on('error', (error) => {
                this.emit('error', error);
            });

            // Initialize the client
            this.client.initialize();
        });
    }

    /**
     * Listen for incoming messages
     * @param {Function} callback - Function to call when a message is received
     * @param {Object} callback.message - Message object with properties: from, body, chat, timestamp, etc.
     */
    listen(callback) {
        if (typeof callback !== 'function') {
            throw new Error('Callback must be a function');
        }

        this.messageHandlers.push(callback);
    }

    /**
     * Send a message
     * @param {string} to - WhatsApp ID (e.g., '1234567890@c.us' for individual, 'xxxxx@g.us' for group)
     * @param {string} message - Message text to send
     * @returns {Promise<Object>} Sent message object
     */
    async send(to, message) {
        if (!this.isReady) {
            throw new Error('Bot is not ready. Call start() first and wait for it to complete.');
        }

        if (!to || !message) {
            throw new Error('Both "to" and "message" parameters are required');
        }

        try {
            const sentMessage = await this.client.sendMessage(to, message);
            return sentMessage;
        } catch (error) {
            throw new Error(`Failed to send message: ${error.message}`);
        }
    }

    /**
     * Stop the bot and disconnect
     * @returns {Promise<void>}
     */
    async stop() {
        if (this.client) {
            await this.client.destroy();
            this.isReady = false;
            this.isStarting = false;
        }
    }

    /**
     * Get all chats
     * @returns {Promise<Array>} Array of chat objects
     */
    async getChats() {
        if (!this.isReady) {
            throw new Error('Bot is not ready');
        }
        return await this.client.getChats();
    }

    /**
     * Get chat by ID
     * @param {string} chatId - Chat ID (e.g., '1234567890@c.us' or 'xxxxx@g.us')
     * @returns {Promise<Object>} Chat object
     */
    async getChat(chatId) {
        if (!this.isReady) {
            throw new Error('Bot is not ready');
        }
        return await this.client.getChatById(chatId);
    }

    /**
     * Internal message handler
     * @private
     */
    async _handleMessage(message) {
        try {
            // Get chat information
            const chat = await message.getChat();

            // Apply group filter if specified
            if (this.options.groupName) {
                if (!chat.isGroup || chat.name !== this.options.groupName) {
                    return; // Skip messages not from the specified group
                }
            }

            // Create simplified message object
            const simplifiedMessage = {
                from: message.from,
                to: message.to,
                body: message.body,
                timestamp: message.timestamp,
                chat: {
                    id: chat.id._serialized,
                    name: chat.name,
                    isGroup: chat.isGroup
                },
                // Original message object for advanced use
                raw: message,
                // Helper method to reply
                reply: async (text) => {
                    return await message.reply(text);
                }
            };

            // Call all registered handlers
            for (const handler of this.messageHandlers) {
                try {
                    await handler(simplifiedMessage);
                } catch (error) {
                    console.error('Error in message handler:', error);
                    this.emit('handler_error', error);
                }
            }
        } catch (error) {
            console.error('Error handling message:', error);
            this.emit('error', error);
        }
    }

    /**
     * Custom event emitter for bot events
     * @private
     */
    emit(event, ...args) {
        if (this.client) {
            this.client.emit(`bot_${event}`, ...args);
        }
    }

    /**
     * Listen for custom bot events
     * @param {string} event - Event name (qr, ready, auth_failure, disconnected, error, handler_error)
     * @param {Function} callback - Event handler
     */
    on(event, callback) {
        if (!this.client) {
            throw new Error('Bot not initialized. Call start() first.');
        }
        this.client.on(`bot_${event}`, callback);
    }
}

module.exports = WhatsAppBot;
