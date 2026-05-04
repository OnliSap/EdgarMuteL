import discord
from discord.ext import commands
from flask import Flask, request, render_template_string
import threading, asyncio, datetime, socket

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
a = 69

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"



HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Admin Panel</title>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: sans-serif; padding: 20px; display: flex; flex-direction: column; align-items: center; margin: 0; }
        .card { background: #1e293b; padding: 25px; border-radius: 20px; border: 2px solid #334155; width: 100%; max-width: 450px; box-sizing: border-box; }
        h2 { color: #6366f1; text-align: center; margin-top: 0; }
        label { color: #94a3b8; font-size: 13px; font-weight: bold; display: block; margin: 15px 0 5px 5px; }
        select, input { width: 100%; background: #0f172a; color: white; border: 2px solid #334155; padding: 14px; border-radius: 12px; font-size: 16px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 16px; border-radius: 12px; border: none; font-weight: bold; font-size: 16px; margin-top: 15px; cursor: pointer; }
        .btn-sync { background: #10b981; color: white; }
        .btn-exec { background: #ef4444; color: white; height: 70px; font-size: 20px; text-transform: uppercase; margin-top: 25px; }
        #status { text-align: center; font-size: 14px; margin-bottom: 15px; color: #10b981; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ADMIN PANEL</h2>
        <div id="status">СИСТЕМА ГОТОВА</div>
        <label>ВЫБЕРИТЕ ЖЕРТВУ:</label>
        <select id="user_box"><option>Загрузка...</option></select>
        <button class="btn-sync" onclick="loadUsers()">ОБНОВИТЬ СПИСОК</button>
        <label>НАКАЗАНИЕ:</label>
        <select id="action_box">
            <option>Тайм-аут</option><option>Откл. микрофон</option><option>Откл. звук</option><option>КИКНУТЬ</option><option>ЗАБАНИТЬ</option>
        </select>
        <label>ВРЕМЯ:</label>
        <select id="time_box">
            <option>30 сек</option><option>1 мин</option><option>5 мин</option><option>30 мин</option><option>1 час</option><option>24 часа</option>
        </select>
        <label>ПРИЧИНА:</label>
        <input type="text" id="reason_input" placeholder="Напиши за что...">
        <button class="btn-exec" onclick="sendCommand()">ИСПОЛНИТЬ</button>
    </div>
    <script>
        async function loadUsers() {
            const res = await fetch('/get_users');
            const data = await res.json();
            const box = document.getElementById('user_box');
            box.innerHTML = '';
            for (const [name, id] of Object.entries(data)) {
                let opt = document.createElement('option');
                opt.value = id; opt.textContent = name;
                box.appendChild(opt);
            }
            document.getElementById('status').innerText = 'ОБНОВЛЕНО';
        }
        async function sendCommand() {
            const data = {
                user_id: document.getElementById('user_box').value,
                action: document.getElementById('action_box').value,
                duration: document.getElementById('time_box').value,
                reason: document.getElementById('reason_input').value || "Без причины"
            };
            await fetch('/execute', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
            alert('Исполнено!');
        }
        window.onload = loadUsers;
    </script>
</body>
</html>
"""


@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)


@app.route('/get_users', methods=['GET'])
def get_users():
    guild = bot.get_guild(GUILD_ID)
    if not guild: return {}, 404
    return {m.display_name: str(m.id) for m in guild.members if not m.bot}, 200


@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    asyncio.run_coroutine_threadsafe(do_action(data), bot.loop)
    return "OK", 200


async def auto_unpunish(member_id, seconds, mode):
    await asyncio.sleep(seconds)
    guild = bot.get_guild(GUILD_ID)
    try:
        member = await guild.fetch_member(member_id)
        if mode == "mic":
            await member.edit(mute=False)
        elif mode == "sound":
            await member.edit(deafen=False)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel: await log_channel.send(f"✅ Срок наказания для {member.mention} истек.")
    except:
        pass


async def do_action(data):
    try:
        guild = bot.get_guild(GUILD_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        member = await guild.fetch_member(int(data['user_id']))
        action, reason, dur_str = data['action'], data['reason'], data['duration']

        seconds = 60
        if "30 сек" in dur_str:
            seconds = 30
        elif "5 мин" in dur_str:
            seconds = 300
        elif "30 мин" in dur_str:
            seconds = 1800
        elif "1 час" in dur_str:
            seconds = 3600
        elif "24 часа" in dur_str:
            seconds = 86400

        until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)

        if action == "Тайм-аут":
            await member.timeout(until, reason=reason)
        elif action == "Откл. микрофон":
            await member.edit(mute=True, reason=reason)
            asyncio.create_task(auto_unpunish(member.id, seconds, "mic"))
        elif action == "Откл. звук":
            await member.edit(deafen=True, reason=reason)
            asyncio.create_task(auto_unpunish(member.id, seconds, "sound"))
        elif action == "КИКНУТЬ":
            await member.kick(reason=reason)
        elif action == "ЗАБАНИТЬ":
            await member.ban(reason=reason)

        embed = discord.Embed(title="ПРИГОВОР ИСПОЛНЕН", color=0xef4444, timestamp=datetime.datetime.now())
        embed.add_field(name="Нарушитель", value=member.mention)
        embed.add_field(name="Мера", value=action)
        embed.add_field(name="Причина", value=reason)
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Ошибка: {e}")


def run_flask():
    local_ip = get_local_ip()
    print(f"\n" + "=" * 40)
    print(f"ПАНЕЛЬ УПРАВЛЕНИЯ ЗАПУЩЕНА!")
    print(f"Адрес для браузера в телефоне: http://{local_ip}:5000")
    print(f"=" * 40 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(TOKEN)