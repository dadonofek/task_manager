/**
 * Simple WhatsApp Bot
 * A minimal, reusable WhatsApp bot package
 *
 * @module simple-whatsapp-bot
 */

const WhatsAppBot = require('./src/WhatsAppBot');

module.exports = WhatsAppBot;

// Also export as default for ES6 imports
module.exports.default = WhatsAppBot;
