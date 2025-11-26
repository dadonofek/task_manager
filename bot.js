/**
 * WhatsApp Task Manager Bot - JSON Edition
 */

const WhatsAppBot = require('./simple-whatsapp-bot');
const fs = require('fs');

const TASKS_JSON = 'tasks.json';
const GROUP_NAME = process.env.WHATSAPP_GROUP || null;

const bot = new WhatsAppBot({
    groupName: GROUP_NAME,
    logQR: true,
    puppeteerOptions: {
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    }
});

// Load tasks from JSON
function loadTasks() {
    try {
        return JSON.parse(fs.readFileSync(TASKS_JSON, 'utf8'));
    } catch (e) {
        return [];
    }
}

// Save tasks to JSON
function saveTasks(tasks) {
    fs.writeFileSync(TASKS_JSON, JSON.stringify(tasks, null, 2));
}

// Parse task from WhatsApp message
function parseTask(text) {
    if (!text.toLowerCase().includes('#task')) return null;
    const now = new Date();
    const task = {
        id: `task_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}_${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}`,
        status: 'open',
        created_at: now.toISOString(),
        completed_at: null
    };
    text.split('\n').forEach(line => {
        if (!line.includes(':') || line.startsWith('#')) return;
        const [k, ...v] = line.split(':');
        const key = k.trim().toLowerCase();
        const val = v.join(':').trim();
        const map = {title:'title', owner:'owner', due:'due', next:'next', priority:'priority'};
        if (map[key]) task[map[key]] = val;
    });
    if (!task.title || !task.owner) return null;
    task.priority = task.priority || 'medium';
    return task;
}

// Format task list for WhatsApp
function formatList(tasks, title = 'Open Tasks') {
    if (!tasks.length) return '📭 No tasks!';
    const p = {high:0, medium:1, low:2};
    tasks.sort((a,b) => (p[a.priority]||1) - (p[b.priority]||1));
    let r = `📋 *${title}*\n\n`;
    tasks.slice(0,10).forEach((t,i) => {
        const e = {high:'🔴', medium:'🟡', low:'🟢'}[t.priority] || '🟡';
        r += `${i+1}. ${e} ${t.title}\n   👤 ${t.owner}`;
        if (t.due) r += ` | 📅 ${t.due}`;
        r += `\n   🆔 ${t.id}\n\n`;
    });
    if (tasks.length > 10) r += `_...${tasks.length-10} more_`;
    return r;
}

async function main() {
    console.log('🤖 WhatsApp Task Manager (JSON)');
    let tasks = loadTasks();
    console.log(`📂 ${tasks.length} tasks loaded\n`);

    await bot.start();
    console.log('✅ Ready! Send #help\n');

    bot.listen(async (msg) => {
        try {
            const b = msg.body.trim();
            console.log(`📨 ${b.substring(0,30)}...`);

            if (b.toLowerCase().includes('#task')) {
                const t = parseTask(b);
                if (!t) return msg.reply('❌ Format:\n#task\nTitle: X\nOwner: Y');
                tasks.push(t);
                saveTasks(tasks);
                msg.reply(`✅ Created!\n📝 ${t.title}\n👤 ${t.owner}\n${t.due?'📅 '+t.due+'\n':''}\n🆔 ${t.id}\n\n#done ${t.id}`);
            }
            else if (b.toLowerCase().match(/#(tasks|list)/)) {
                tasks = loadTasks();
                msg.reply(formatList(tasks.filter(t => t.status === 'open')));
            }
            else if (b.toLowerCase().includes('#mine')) {
                const owner = b.split(/\s+/).find((w,i,a) => i>0 && a[i-1].toLowerCase()==='#mine');
                if (!owner) return msg.reply('❓ #mine <name>');
                tasks = loadTasks();
                const mine = tasks.filter(t => t.status==='open' && t.owner.toLowerCase()===owner.toLowerCase());
                msg.reply(formatList(mine, `Tasks for ${owner}`));
            }
            else if (b.toLowerCase().includes('#done')) {
                const id = b.split(/\s+/).find(w => w.startsWith('task_'));
                if (!id) return msg.reply('❓ #done task_xxx');
                tasks = loadTasks();
                const t = tasks.find(x => x.id === id);
                if (!t) return msg.reply(`❌ Not found: ${id}`);
                t.status = 'done';
                t.completed_at = new Date().toISOString();
                saveTasks(tasks);
                msg.reply(`✅ Done!\n📝 ${t.title}\n👤 ${t.owner}`);
            }
            else if (b.toLowerCase() === '#help') {
                msg.reply(`📝 *Task Manager*\n\n*Create:*\n#task\nTitle: X\nOwner: Y\nDue: Z\nPriority: high/medium/low\n\n*List:*\n#tasks\n#mine <name>\n\n*Done:*\n#done task_xxx`);
            }
        } catch(e) {
            console.error('❌', e);
        }
    });
}

process.on('SIGINT', async () => { await bot.stop(); process.exit(); });
main();
