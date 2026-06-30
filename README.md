# 🛡️ EdgarMuteL - Discord Admin Action Panel v4.1

An advanced, dual-interface administration panel designed for Discord server moderators. This ecosystem combines a mobile-friendly **Flask web interface** for remote phone management and a native **PySide6 (Qt) desktop application** for monitoring directly from your Mac workstation.

---

## 🏗️ System Architecture

The application runs three highly synchronized layers in parallel from a single launch:

1. **The Main Core Engine (`bot.py`):** **This is the main entry point of the entire project.** Running this script initializes the asynchronous `discord.ext.commands.Bot` engine. On the very first boot, it opens the initialization setup wizard; on subsequent runs, it launches the Discord backend and spins up a separate thread for the web gateway.
2. **The Web Gateway Layer:** A background-threaded Flask microservice running a responsive HTML/JavaScript dashboard. It acts as a network bridge, allowing administrators to issue moderation overrides (timeouts, mutes, kicks, bans) directly from a mobile phone browser over the local network.
3. **The Workstation UI (`main.py`):** A custom PySide6 Qt GUI desktop application launched dynamically by the main engine. It features a high-speed polling loop (`QtCore.QTimer`) that queries the Flask web server to verify status connections and dynamically populate the active server user list.

---

## 🎯 Key Features

* **Single Script Execution:** Launch everything—the bot, the web server, and the desktop frame—by running just one file.
* **Cross-Platform Control:** Issue moderation commands from your phone browser or manage them directly via your Mac desktop panel.
* **Unified Sentence Panel:** Instant dropdown controls for Timeouts, Voice Mutes, Deafens, Kicks, and Bans.
* **Automated Unpunish:** Asynchronous background timers handling the automatic lift of temporary voice and audio restrictions.
* **First-Run Configuration Wizard:** A clean GUI wizard (`FirstStartupWindow`) that automatically prompts you to initialize your Bot Token and Server IDs on deployment, saving them securely to a local file.

---

## 🚀 Installation & Local Deployment
* MacOS users might need to allow the app to act in their device settings before launching it

### 📋 Prerequisites
* Python 3.10+
* A verified Discord Bot Token ([Discord Developer Portal](https://discord.com))

### 🛠️ Setup Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/OnliSap/EdgarMuteL
   cd EdgarMuteL
   ```

2. **Initialize Your Virtual Environment & Dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install discord.py flask PySide6 requests
   ```

3. **Launch the Application:**
   Always run the primary script to boot up the system architecture:
   ```bash
   python bot.py
   ```
   *(Note: If this is your first startup, a setup window will open. Enter your Bot Token, Guild ID, and Log Channel ID, save the configurations, and restart the script).*

---
*Developed by [@tishaker]([https://github.com](https://github.com/tishaker)). This repository tracks advanced modular extension testing, network port routing configurations, and custom automation interfaces.*
