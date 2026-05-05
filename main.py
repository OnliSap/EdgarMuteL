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
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(35, 25, 35, 25)
        self.layout.setSpacing(10)
        
        # Create UI elements
        self.header = QtWidgets.QLabel("STATUS: SYNCING...")
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.header)

        self.user_box = QtWidgets.QComboBox()
        self.layout.addWidget(self.user_box)

        self.action_box = QtWidgets.QComboBox()
        self.action_box.addItems(["Тайм-аут", "Откл. микрофон", "Откл. звук", "КИКНУТЬ", "ЗАБАНИТЬ"])
        self.layout.addWidget(self.action_box)

        self.time_box = QtWidgets.QComboBox()
        self.time_box.addItems(["30 сек", "1 мин", "5 мин", "30 мин", "1 час", "24 часа", "Навсегда"])
        self.layout.addWidget(self.time_box)

        self.reason_input = QtWidgets.QLineEdit()
        self.reason_input.setPlaceholderText("За что наказываем?")
        self.layout.addWidget(self.reason_input)

        self.layout.addStretch()

        self.btn_sync = DecoButton("ОБНОВИТЬ СПИСОК", "#10b981", fsize=12)
        self.btn_exec = DecoButton("ИСПОЛНИТЬ ПРИГОВОР", "#ef4444")
        self.btn_exec.setFixedSize(380, 60)
        self.layout.addWidget(self.btn_sync, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.btn_exec, alignment=QtCore.Qt.AlignCenter)

        self.btn_sync.clicked.connect(self.fetch_users)
        self.btn_exec.clicked.connect(self.send_command)

        theme_btn = DecoButton("СМЕНИТЬ ТЕМУ", "#64748b", fsize=10)
        theme_btn.setFixedSize(190, 30)
        theme_btn.clicked.connect(self.change_theme_written)
        self.layout.addWidget(theme_btn, alignment=QtCore.Qt.AlignRight)
        
        self.user_data = {}
        self.set_styles()
        QtCore.QTimer.singleShot(1000, self.fetch_users)
        
        
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
            
    
    def set_styles(self):
        # Background
        self.setStyleSheet(f"QWidget {{ background-color: {config[self.style_type]['background']}; }}")
        
        # ComboBox style
        combo_style = f"""
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
        
        self.header.setStyleSheet(f"color: {config[self.style_type]['header_color']}; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        self.user_box.setStyleSheet(combo_style)
        self.action_box.setStyleSheet(combo_style)
        self.time_box.setStyleSheet(combo_style)
        self.reason_input.setStyleSheet(f"QLineEdit {{ {config[self.style_type]['qlineedit']} }}")
        
        # Update labels in layout
        label_style = f"color: {config[self.style_type]['label_color']}; font-weight: bold; font-size: 12px; margin-top: 5px;"
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QLabel) and widget != self.header:
                widget.setStyleSheet(label_style)
            
    def change_theme_written(self):
        self.theme_index = (self.theme_index + 1) % 2
        self.style_type = themes[self.theme_index]
        theme_change(config, self.theme_index)
        self.set_styles()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())