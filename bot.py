import discord, time, subprocess, sys, threading, asyncio, datetime, socket, os
from discord.ext import commands
from flask import Flask, request, render_template_string
from btn import DecoButton
from ini_parser import get_bot_config, get_config_path
from PySide6 import QtWidgets, QtCore
from main import MainWindow
window = MainWindow

def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


botset = get_bot_config()

TOKEN = botset['bot'].get('token', '').strip()
GUILD_ID = safe_int(botset['bot'].get('guild_id', '0'))
LOG_CHANNEL_ID = safe_int(botset['bot'].get('log_channel_id', '0'))
first_startup = botset['bot'].getboolean('first_startup', fallback=True)

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
app = Flask(__name__)


def should_launch_gui():
    if getattr(sys, "frozen", False):
        return True
    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    return os.path.exists(main_script)


def get_gui_lock_path():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ".edgarmute_gui.lock")


def is_gui_process_running(lock_path):
    if not os.path.exists(lock_path):
        return False

    try:
        with open(lock_path, "r", encoding="utf-8") as handle:
            pid_text = handle.read().strip()
        if not pid_text:
            return False
        pid = int(pid_text)
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        try:
            os.remove(lock_path)
        except OSError:
            pass
        return False
    except (ValueError, PermissionError, OSError):
        return False


def launch_gui_subprocess(lock_path=None):
    if lock_path is None:
        lock_path = get_gui_lock_path()

    if is_gui_process_running(lock_path):
        print("GUI already running, skipping duplicate launch")
        return False

    if getattr(sys, "frozen", False):
        try:
            app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
            window = MainWindow()
            window.show()
            with open(lock_path, "w", encoding="utf-8") as handle:
                handle.write(str(os.getpid()))
            return app
        except Exception as exc:
            print(f"Failed to launch GUI window: {exc}")
            return False

    main_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
    if not os.path.exists(main_script):
        return False

    try:
        process = subprocess.Popen([sys.executable, main_script], cwd=os.path.dirname(os.path.abspath(__file__)))
        with open(lock_path, "w", encoding="utf-8") as handle:
            handle.write(str(process.pid))
    except OSError:
        return False

    return True


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
            <option>30 сек</option><option>1 мин</option><option>5 мин</option><option>30 мин</option><option>1 час</option><option>24 часа</option><option>Максимум(28 дней)</option>
        </select>
        <label>ПРИЧИНА:</label>
        <input type="text" id="reason_input" placeholder="Напиши за что...">
        <button class="btn-exec" onclick="sendCommand()">ИСПОЛНИТЬ</button>
    </div>
    <script>
        async function loadUsers() {
            const res = await fetch('/get_users');
            if (!res.ok) {
                document.getElementById('status').innerText = 'ОШИБКА ЗАГРУЗКИ';
                return;
            }
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
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/get_users', methods=['GET'])
def get_users():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return {}, 200
    return {m.display_name: str(m.id) for m in guild.members if not m.bot}, 200


@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    if not data:
        return "Bad Request", 400
    asyncio.run_coroutine_threadsafe(do_action(data), bot.loop)
    return "OK", 200


async def auto_unpunish(member_id, seconds, mode):
    await asyncio.sleep(seconds)
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    try:
        member = await guild.fetch_member(member_id)
        if mode == "mic":
            await member.edit(mute=False)
        elif mode == "sound":
            await member.edit(deafen=False)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"✅ Срок наказания для {member.mention} истек.")
    except Exception:
        pass


async def do_action(data):
    try:
        guild = bot.get_guild(GUILD_ID)
        if not guild:
            print("Ошибка: сервер не найден")
            return

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        member = await guild.fetch_member(int(data['user_id']))
        action, reason, dur_str = data['action'], data['reason'], data['duration']

        seconds = 60
        if "30 сек" in dur_str:
            seconds = 30
        elif "1 мин" in dur_str:
            seconds = 60
        elif "5 мин" in dur_str:
            seconds = 300
        elif "30 мин" in dur_str:
            seconds = 1800
        elif "1 час" in dur_str:
            seconds = 3600
        elif "24 часа" in dur_str:
            seconds = 86400
        elif "Максимум(28 дней)" in dur_str:
            seconds = 2419199

        if action == "Тайм-аут":
            await member.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=seconds), reason=reason)
        elif action == "Откл. микрофон":
            await member.edit(mute=True, reason=reason)
            bot.loop.create_task(auto_unpunish(member.id, seconds, "mic"))
        elif action == "Откл. звук":
            await member.edit(deafen=True, reason=reason)
            bot.loop.create_task(auto_unpunish(member.id, seconds, "sound"))
        elif action == "КИКНУТЬ":
            await member.kick(reason=reason)
        elif action == "ЗАБАНИТЬ":
            await member.ban(reason=reason)
        else:
            print(f"Ошибка: неизвестное действие {action}")
            return

        if log_channel:
            embed = discord.Embed(title="ПРИГОВОР ИСПОЛНЕН", color=0xef4444, timestamp=datetime.datetime.now())
            embed.add_field(name="Нарушитель", value=member.mention)
            embed.add_field(name="Мера", value=action)
            embed.add_field(name="Причина", value=reason)
            await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Ошибка: {e}")


class FirstStartupWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Первый запуск бота")
        self.setFixedSize(400, 260)
        label = QtWidgets.QLabel("Похоже, что это первый запуск бота.\nПожалуйста, заполните данные и перезапустите программу.")
        label.setAlignment(QtCore.Qt.AlignCenter)

        layout_token = QtWidgets.QHBoxLayout()
        token_getter = QtWidgets.QLineEdit()
        token_line = QtWidgets.QLabel("Введите токен бота:")
        token_getter.setPlaceholderText("тут последовательность какая-то")
        layout_token.addWidget(token_line)
        layout_token.addWidget(token_getter)

        layout_guild = QtWidgets.QHBoxLayout()
        guild_getter = QtWidgets.QLineEdit()
        guild_line = QtWidgets.QLabel("Введите ID сервера:")
        guild_getter.setPlaceholderText("тут число")
        layout_guild.addWidget(guild_line)
        layout_guild.addWidget(guild_getter)

        layout_log_channel = QtWidgets.QHBoxLayout()
        log_channel_getter = QtWidgets.QLineEdit()
        log_channel_line = QtWidgets.QLabel("Введите ID канала для логов:")
        log_channel_getter.setPlaceholderText("тут тоже число")
        layout_log_channel.addWidget(log_channel_line)
        layout_log_channel.addWidget(log_channel_getter)

        btn_save = DecoButton("СОХРАНИТЬ", "#10b981")
        btn_save.clicked.connect(lambda: self.get_data(token_getter.text(), guild_getter.text(), log_channel_getter.text()))

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(layout_token)
        main_layout.addLayout(layout_guild)
        main_layout.addLayout(layout_log_channel)
        main_layout.addWidget(btn_save, 
                              alignment=QtCore.Qt.AlignCenter)

        self.setLayout(main_layout)

    @QtCore.Slot()
    def get_data(self, token, guild_id, log_channel_id):
        token = token.strip()
        guild_id = guild_id.strip()
        log_channel_id = log_channel_id.strip()

        if not token or not guild_id.isdigit() or not log_channel_id.isdigit():
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                "Проверьте токен и числовые поля."
            )
            return

        botset['bot']['token'] = token
        botset['bot']['guild_id'] = guild_id
        botset['bot']['log_channel_id'] = log_channel_id
        botset['bot']['first_startup'] = "False"
        config_path = get_config_path("bot_settings.ini")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as configfile:
            botset.write(configfile)

        QtWidgets.QMessageBox.information(self, "Сохранено", "Данные сохранены! Пожалуйста, перезапустите программу.")
        self.close()


def run_flask():
    local_ip = get_local_ip()
    print(f"\n" + "=" * 40)
    print(f"ПАНЕЛЬ УПРАВЛЕНИЯ ЗАПУЩЕНА!")
    print(f"Адрес для браузера в телефоне: http://{local_ip}:8000")
    print(f"=" * 40 + "\n")
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)


if __name__ == "__main__" and not first_startup:
    if not TOKEN:
        print("Bot token is not configured. Заполните bot_settings.ini.")
        sys.exit(1)

    if getattr(sys, "frozen", False):
        threading.Thread(target=run_flask, daemon=True).start()
        threading.Thread(target=lambda: bot.run(TOKEN), daemon=True).start()

        app = QtWidgets.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    if should_launch_gui():
        launch_gui_subprocess()

    threading.Thread(target=run_flask, daemon=True).start()
    
    bot.run(TOKEN)
    
elif __name__ == "__main__" and first_startup:
    app = QtWidgets.QApplication(sys.argv)
    window = FirstStartupWindow()
    window.show()
    sys.exit(app.exec())