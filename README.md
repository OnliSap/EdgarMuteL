# 🛡️ EdgarMuteL - Discord Admin Action Panel v4.1

An advanced, dual-interface administration panel designed for Discord server moderators. This project features a synchronous ecosystem combining a mobile-friendly **Flask web interface** for on-the-go management and a native **PySide6 (Qt) desktop application** for full monitoring right from a Mac workstation.

---

## 🏗️ System Architecture

The project splits functionality into three main layers running in parallel:
1. **The Discord Engine (`bot.py`):** An asynchronous bot backend managing token validation, logging channels, and core API interactions (timeouts, bans, kicks, mutes).
2. **The Web Gateway Layer:** A background threaded Flask microservice running a responsive mobile UI web template. It acts as an API bridge allowing administrators to issue server sentences from a phone browser over the local network.
3. **The Workstation UI (`main.py`):** A custom PySide6 Qt GUI application that runs locally. It uses a high-speed polling timer loop (`QtCore.QTimer`) to constantly query the local web gateway, update active server user lists, and check system status signals.

---

## 🎯 Key Features

* **Cross-Platform Control:** Manage your server from either a native Mac app window or any local network phone browser.
* **Unified Enforcement Panel:** Quick dropdown triggers for Timeouts, Mutes, Deafens, Kicks, and Bans.
* **Smart Auto-Unpunish:** Automatic countdown loops handling the removal of temporary microphone or audio restrictions.
* **Robust Theme Engine:** Quick theme index changes built right into the local configuration settings (`ini_parser.py`).
* **First-Run Configuration Wizard:** A clean, built-in setup window (`FirstStartupWindow`) that initializes your bot token and server IDs securely on deployment.

---

## 🚀 Installation & Local Deployment

### 📋 Prerequisites
* Python 3.10+
* A verified Discord Bot Token ([Discord Developer Portal](https://discord.com))

### 🛠️ Setup Steps
1. **Clone and Navigate:**
   ```bash
   git clone https://github.com
   cd EdgarMuteL
   ```

2. **Initialize Environment & Dependencies:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install discord.py flask PySide6 requests
   ```

3. **Run the Initialization Wizard:**
   Launch the entry script to open the onboarding configuration manager:
   ```bash
   python 1ai_dumb.py
   ```
   *(Enter your Bot Token, Guild ID, and Log Channel ID into the fields, click Save, and restart).*

---
*Developed by [@tishaker](https://github.com). This repository tracks ongoing feature updates, security optimization routines, and modular extensions.*
