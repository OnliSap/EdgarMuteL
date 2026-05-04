import sys, requests
from PySide6 import QtWidgets, QtCore
from btn import DecoButton
from config_loader import get_config, theme_change

config = get_config()
themes = ["dark_theme", "white_theme"]

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.bot_url = "http://127.0.0.1:5000"
        self.setWindowTitle("Admin Panel v4.0")
        self.setFixedSize(450, 750)
        
        self.theme_index = int(config['user']['theme_index'])
        self.style_type = themes[self.theme_index]
        
        
        self.setStyleSheet(f"QWidget {{ background-color: {config[self.style_type]['background']}; }}")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(35, 25, 35, 25)
        layout.setSpacing(10)
        
        # ПОЛНОСТЬЮ ТЕМНЫЙ СТИЛЬ ДЛЯ СПИСКОВ
        dark_combo_style = f"""
            QComboBox {{ 
                {config[self.style_type]['qcombobox']} 
            }}
            QComboBox::drop-down {{ 
                border: 0px; 
            }}
            QComboBox::down-arrow {{ 
                {config[self.style_type]['qcombobox_downarrow']} 
            }}
            QComboBox QAbstractItemView {{
                {config[self.style_type]['qcombobox_menu']}
            }}
        """

        self.header = QtWidgets.QLabel("STATUS: SYNCING...")
        self.header.setStyleSheet(f"color: {config[self.style_type]['header_color']}; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.header)

        def create_label(text):
            lbl = QtWidgets.QLabel(text)
            lbl.setStyleSheet(f"color: {config[self.style_type]['label_color']}; font-weight: bold; font-size: 12px; margin-top: 5px;")
            return lbl

        layout.addWidget(create_label("ВЫБЕРИТЕ ЖЕРТВУ:"))
        self.user_box = QtWidgets.QComboBox()
        self.user_box.setStyleSheet(dark_combo_style)
        layout.addWidget(self.user_box)

        layout.addWidget(create_label("ТИП НАКАЗАНИЯ:"))
        self.action_box = QtWidgets.QComboBox()
        self.action_box.addItems(["Тайм-аут", "Откл. микрофон", "Откл. звук", "КИКНУТЬ", "ЗАБАНИТЬ"])
        self.action_box.setStyleSheet(dark_combo_style)
        layout.addWidget(self.action_box)

        layout.addWidget(create_label("ВРЕМЯ:"))
        self.time_box = QtWidgets.QComboBox()
        self.time_box.addItems(["30 сек", "1 мин", "5 мин", "30 мин", "1 час", "24 часа", "Навсегда"])
        self.time_box.setStyleSheet(dark_combo_style)
        layout.addWidget(self.time_box)

        layout.addWidget(create_label("ПРИЧИНА:"))
        self.reason_input = QtWidgets.QLineEdit()
        self.reason_input.setPlaceholderText("За что наказываем?")
        self.reason_input.setStyleSheet(f"QLineEdit {{ {config[self.style_type]['qlineedit']} }}")
        layout.addWidget(self.reason_input)

        layout.addStretch()

        self.btn_sync = DecoButton("ОБНОВИТЬ СПИСОК", "#10b981", fsize=12)
        self.btn_exec = DecoButton("ИСПОЛНИТЬ ПРИГОВОР", "#ef4444")
        self.btn_exec.setFixedSize(380, 60)
        
        layout.addWidget(self.btn_sync, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.btn_exec, alignment=QtCore.Qt.AlignCenter)

        self.btn_sync.clicked.connect(self.fetch_users)
        self.btn_exec.clicked.connect(self.send_command)

        self.user_data = {}
        QtCore.QTimer.singleShot(1000, self.fetch_users)
        
        theme_btn = DecoButton("СМЕНИТЬ ТЕМУ", "#64748b", fsize=8)
        theme_btn.clicked.connect(self.change_theme_written)
        layout.addWidget(theme_btn, alignment=QtCore.Qt.AlignRight)
        
        
    def fetch_users(self):
        try:
            r = requests.get(f"{self.bot_url}/get_users", timeout=2)
            self.user_data = r.json()
            self.user_box.clear()
            self.user_box.addItems(self.user_data.keys())
            self.header.setText("STATUS: ONLINE")
            self.header.setStyleSheet("color: #10b981; font-weight: bold;")
        except:
            self.header.setText("STATUS: BOT OFFLINE")
            self.header.setStyleSheet("color: #ef4444; font-weight: bold;")

    def send_command(self):
        user_name = self.user_box.currentText()
        if not user_name: return
        data = {
            "user_id": self.user_data[user_name],
            "action": self.action_box.currentText(),
            "duration": self.time_box.currentText(),
            "reason": self.reason_input.text() or "Без причины"
        }
        try:
            requests.post(f"{self.bot_url}/execute", json=data, timeout=2)
            self.header.setText(f"SUCCESS: {user_name.upper()}")
            QtCore.QTimer.singleShot(3000, lambda: self.header.setText("STATUS: ONLINE"))
        except:
            self.header.setText("SEND ERROR")
            
            
    def change_theme_written(self):
        self.theme_index = (self.theme_index + 1) % 2 # only black an white now
        self.style_type = themes[self.theme_index]
        theme_change(config, self.theme_index)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())