from PySide6 import QtWidgets

class DecoButton(QtWidgets.QPushButton):
    def __init__(self, btext, colour, fsize=14):
        super().__init__(btext)
        self.setFixedSize(280, 50)
        self.colour = colour
        self.fsize = fsize
        self.update_style()

    def update_style(self, new_colour=None):
        if new_colour: self.colour = new_colour
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e293b;
                color: #f8fafc;
                border: 3px solid {self.colour};
                border-radius: 12px;
                font-weight: bold;
                font-size: {self.fsize}px;
            }}
            QPushButton:hover {{ 
                background-color: {self.colour}; 
                color: white; 
            }}
            QPushButton:pressed {{ background-color: #0f172a; }}
        """)