import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QLabel, QDialog, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt, QUrl, QRect
from PyQt6.QtGui import QIcon, QLinearGradient, QPalette, QColor, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from game_window import HanoiTowersGame

class RulesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Правила игры")
        self.setFixedSize(600, 400)
        
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
        
        rules_font = QFont()
        rules_font.setPointSize(12)
        
        scroll = QScrollArea()
        rules_label = QLabel(rules_text)
        rules_label.setFont(rules_font)
        rules_label.setStyleSheet("background: transparent; color: white;")
        rules_label.setWordWrap(True)
        scroll.setWidget(rules_label)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(scroll)

        button_font = QFont()
        button_font.setPointSize(12)
        
        menu_button = QPushButton("Меню")
        menu_button.setFont(button_font)
        menu_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
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
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

class RecordsDialog(QDialog):
    def __init__(self, records):
        super().__init__()
        self.setWindowTitle("Рекорды")
        self.setFixedSize(400, 400)
        
        self.set_gradient_background()
        
        self.records = records
        
        main_layout = QVBoxLayout()
        
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        
        title_label = QLabel("Рекорды по уровням:")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; background: transparent;")
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(15)
        
        records_font = QFont()
        records_font.setPointSize(12)
        
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
        records_label.setFont(records_font)
        records_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        records_label.setStyleSheet("color: white; background: transparent;")
        content_layout.addWidget(records_label)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        main_layout.addSpacing(15)
        
        button_font = QFont()
        button_font.setPointSize(12)
        
        menu_button = QPushButton("Меню")
        menu_button.setFont(button_font)
        menu_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
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
        self.last_geometry = self.geometry()
        
        self.set_gradient_background()
        
        self.main_layout = QVBoxLayout()
        
        title_label = QLabel("Ханойские башни")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        title_font = QFont()
        title_font.setPointSize(36)
        title_font.setBold(True)
        title_font.setFamily("Arial")
        title_label.setFont(title_font)
        
        self.main_layout.addSpacing(50)
        self.main_layout.addWidget(title_label)
        self.main_layout.addSpacing(50)

        button_font = QFont()
        button_font.setPointSize(16)
        
        self.play_button = QPushButton("Играть")
        self.play_button.setFont(button_font)
        
        self.rules_button = QPushButton("Правила игры")
        self.rules_button.setFont(button_font)
        
        self.records_button = QPushButton("Рекорды")
        self.records_button.setFont(button_font)
        
        self.exit_button = QPushButton("Выход")
        self.exit_button.setFont(button_font)

        button_style = """
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 12px;
                border-radius: 6px;
                min-width: 200px;
                min-height: 50px;
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
        self.game_window.main_window = self
        self.game_window.return_to_menu.connect(self.return_to_menu)
        # Устанавливаем такой же размер, как у главного окна
        self.game_window.setGeometry(self.geometry())
        self.hide()
        self.game_window.show()

    def return_to_menu(self):
        # Сохраняем размер игрового окна перед возвратом
        self.last_geometry = self.game_window.geometry()
        self.game_window.close()
        # Восстанавливаем размер главного окна
        self.setGeometry(self.last_geometry)
        self.show()

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

    def closeEvent(self, event):
        self.last_geometry = self.geometry()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())