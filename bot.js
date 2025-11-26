/**
 * WhatsApp Task Manager Bot - Compact Edition
 */

const WhatsAppBot = require('./simple-whatsapp-bot');
const { spawn } = require('child_process');
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

function runPython(script, args = []) {
    return new Promise((resolve, reject) => {
        const python = spawn('python3', ['-c', script, ...args]);
        let stdout = '';
        let stderr = '';
        python.stdout.on('data', (d) => stdout += d.toString());
        python.stderr.on('data', (d) => stderr += d.toString());
        python.on('close', (code) => {
            code !== 0 ? reject(new Error(stderr)) : resolve(stdout.trim());
        });
    });
}

async function createTask(task) {
    const code = 'import json, sys; sys.path.insert(0, "."); import apple_notes; t = json.loads(sys.argv[1]); print(json.dumps(apple_notes.create_task(t)))';
    try {
        return JSON.parse(await runPython(code, [JSON.stringify(task)]));
    } catch (e) {
        console.error('⚠️ Notes unavailable');
        return task;
    }
}

async function getAllTasks() {
    const code = 'import json, sys; sys.path.insert(0, "."); import apple_notes; print(json.dumps(apple_notes.get_all_tasks()))';
    try {
        return JSON.parse(await runPython(code));
    } catch (e) {
        return JSON.parse(fs.readFileSync(TASKS_JSON, 'utf8') || '[]');
    }
}

async function markTaskDone(taskId) {
    const code = 'import json, sys; sys.path.insert(0, "."); import apple_notes; print(json.dumps({"ok": apple_notes.mark_done(sys.argv[1])}))';
    try {
        return JSON.parse(await runPython(code, [taskId])).ok;
    } catch (e) {
        return false;
    }
}

function saveJSON(tasks) {
    fs.writeFileSync(TASKS_JSON, JSON.stringify(tasks, null, 2));
}

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
    console.log('🤖 WhatsApp Task Manager');
    let cache = [];
    try { cache = JSON.parse(fs.readFileSync(TASKS_JSON, 'utf8')); } catch(e) {}
    console.log(`📂 ${cache.length} tasks loaded\n`);

    await bot.start();
    console.log('✅ Ready! Send #help\n');

    setInterval(async () => {
        try {
            cache = await getAllTasks();
            saveJSON(cache);
            console.log(`🔄 Synced ${cache.length} tasks`);
        } catch(e) {}
    }, 5*60*1000);

    bot.listen(async (msg) => {
        try {
            const b = msg.body.trim();
            console.log(`📨 ${b.substring(0,30)}...`);

            if (b.toLowerCase().includes('#task')) {
                const t = parseTask(b);
                if (!t) return msg.reply('❌ Format:\n#task\nTitle: X\nOwner: Y');
                const created = await createTask(t);
                cache.push(created);
                saveJSON(cache);
                msg.reply(`✅ Created!\n📝 ${t.title}\n👤 ${t.owner}\n${t.due?'📅 '+t.due+'\n':''}\n🆔 ${t.id}\n\n#done ${t.id}`);
            }
            else if (b.toLowerCase().match(/#(tasks|list)/)) {
                cache = await getAllTasks();
                saveJSON(cache);
                msg.reply(formatList(cache.filter(t => t.status === 'open')));
            }
            else if (b.toLowerCase().includes('#mine')) {
                const owner = b.split(/\s+/).find((w,i,a) => i>0 && a[i-1].toLowerCase()==='#mine');
                if (!owner) return msg.reply('❓ #mine <name>');
                cache = await getAllTasks();
                const mine = cache.filter(t => t.status==='open' && t.owner.toLowerCase()===owner.toLowerCase());
                msg.reply(formatList(mine, `Tasks for ${owner}`));
            }
            else if (b.toLowerCase().includes('#done')) {
                const id = b.split(/\s+/).find(w => w.startsWith('task_'));
                if (!id) return msg.reply('❓ #done task_xxx');
                const t = cache.find(x => x.id === id);
                if (!t) return msg.reply(`❌ Not found: ${id}`);
                await markTaskDone(id);
                t.status = 'done';
                t.completed_at = new Date().toISOString();
                saveJSON(cache);
                msg.reply(`✅ Done!\n📝 ${t.title}\n👤 ${t.owner}`);
            }
            else if (b.toLowerCase() === '#help') {
                msg.reply(`📝 *Task Manager*\n\n*Create:*\n#task\nTitle: X\nOwner: Y\nDue: Z\n\n*List:*\n#tasks\n#mine <name>\n\n*Done:*\n#done task_xxx`);
            }
        } catch(e) {
            console.error('❌', e);
        }
    });
}

process.on('SIGINT', async () => { await bot.stop(); process.exit(); });
main();
