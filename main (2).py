import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QLabel, QDialog, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QLinearGradient, QPalette, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from game_window import HanoiTowersGame

class RulesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Правила игры")
        self.setGeometry(100, 100, 600, 300)
        
        self.set_gradient_background()
        
        rules_text = """Правила игры "Ханойские башни":
1. Начальная позиция: все диски располагаются на одном из стержней (обычно на левом)
в порядке убывания размера, то есть самый большой диск внизу, а самый маленький — сверху;
2. Перемещение дисков: игрок может перемещать только один диск за раз. 
Диск можно взять с верхней части стержня и переместить его на другой стержень. 
Перемещать диски можно, зажав определённый диск и перенести 
его на новую позицию с помощью мыши и\или "тачпада";
3. Запрет на размещение: никогда нельзя помещать больший диск на меньший. 
Диски должны всегда располагаться в порядке убывания размера;
4. Цель перемещения: игрок должен переместить все диски на другой стержень за 
минимальное количество времени (обычно на правый).
"""
        layout = QVBoxLayout()
        scroll = QScrollArea()
        rules_label = QLabel(rules_text)
        rules_label.setStyleSheet("background: transparent; color: white;")
        scroll.setWidget(rules_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(scroll)

        menu_button = QPushButton("Меню")
        menu_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)
        menu_button.clicked.connect(self.accept)
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
    
    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(75, 0, 130))  # Фиолетовый
        gradient.setColorAt(1, QColor(25, 25, 112))  # Темно-синий
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

class RecordsDialog(QDialog):
    def __init__(self, records):
        super().__init__()
        self.setWindowTitle("Рекорды")
        self.setGeometry(100, 100, 400, 300)
        
        self.set_gradient_background()
        
        self.records = records
        
        main_layout = QVBoxLayout()
        
        title_label = QLabel("Рекорды по уровням:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: white;
            background: transparent;
        """)
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        records_text = ""
        for level, data in sorted(self.records.items(), key=lambda x: int(x[0])):
            if isinstance(data, dict):
                time = data.get('time', 0)
            else:
                time = data
                
            minutes = time // 60
            seconds = time % 60
            records_text += f"Уровень {level}: {minutes:02}:{seconds:02}\n"
        
        if not records:
            records_text = "Рекорды пока не установлены"
            
        records_label = QLabel(records_text)
        records_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        records_label.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(records_label)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        main_layout.addSpacing(20)
        menu_button = QPushButton("Меню")
        menu_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)
        menu_button.clicked.connect(self.accept)
        main_layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)
    
    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ханойские башни")
        self.setGeometry(100, 100, 800, 600)
        
        self.set_gradient_background()
        
        self.main_layout = QVBoxLayout()

        self.play_button = QPushButton("Играть")
        self.rules_button = QPushButton("Правила игры")
        self.records_button = QPushButton("Рекорды")
        self.exit_button = QPushButton("Выход")

        button_style = """
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                min-width: 200px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """
        
        self.play_button.setStyleSheet(button_style)
        self.rules_button.setStyleSheet(button_style)
        self.records_button.setStyleSheet(button_style)
        self.exit_button.setStyleSheet(button_style)

        self.play_button.clicked.connect(self.start_game)
        self.rules_button.clicked.connect(self.show_rules)
        self.records_button.clicked.connect(self.show_records)
        self.exit_button.clicked.connect(self.close)

        self.main_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.rules_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.records_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.main_layout)
    
    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

    def start_game(self):
        self.game_window = HanoiTowersGame()
        self.game_window.return_to_menu.connect(self.show)
        self.game_window.show()
        self.hide()

    def show_rules(self):
        dialog = RulesDialog()
        dialog.exec()

    def show_records(self):
        try:
            with open('records.json', 'r') as f:
                records = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            records = {}
            
        dialog = RecordsDialog(records)
        dialog.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_width = self.width() // 4
        self.play_button.setFixedWidth(new_width)
        self.rules_button.setFixedWidth(new_width)
        self.records_button.setFixedWidth(new_width)
        self.exit_button.setFixedWidth(new_width)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())