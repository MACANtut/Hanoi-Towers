import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QDialog, QScrollArea, QHBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Импортируем класс HanoiTowersGame из game_window.py
from game_window import HanoiTowersGame

# Глобальный медиаплеер для фоновой музыки
global_media_player = None

class RulesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Правила игры")
        self.setGeometry(100, 100, 600, 300)

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
        scroll.setWidget(rules_label)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        menu_button = QPushButton("Меню")
        menu_button.clicked.connect(self.accept)
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)  # Выравнивание кнопки по центру

        self.setLayout(layout)

class RecordsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Рекорды")
        self.setGeometry(100, 100, 400, 200)

        records_text = "Здесь будут ваши рекорды:\n\n1. Игрок 1 - 10 ходов\n2. Игрок 2 - 15 ходов"
        layout = QVBoxLayout()
        records_label = QLabel(records_text)
        layout.addWidget(records_label)

        menu_button = QPushButton("Меню")
        menu_button.clicked.connect(self.accept)
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)  # Выравнивание кнопки по центру

        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ханойские башни")
        self.setGeometry(100, 100, 1000, 800)
        
        # Основной layout
        self.main_layout = QVBoxLayout()

        # Создание кнопок
        self.play_button = QPushButton("Играть")
        self.rules_button = QPushButton("Правила игры")
        self.records_button = QPushButton("Рекорды")
        self.exit_button = QPushButton("Выход")

        # Установка начальной ширины для кнопок
        self.button_width = 200  # Начальная ширина кнопок
        self.play_button.setFixedWidth(self.button_width)
        self.rules_button.setFixedWidth(self.button_width)
        self.records_button.setFixedWidth(self.button_width)
        self.exit_button.setFixedWidth(self.button_width)

        # Подключение кнопок к функциям
        self.play_button.clicked.connect(self.start_game)
        self.rules_button.clicked.connect(self.show_rules)
        self.records_button.clicked.connect(self.show_records)
        self.exit_button.clicked.connect(self.close)

        # Добавление кнопок с выравниванием по центру
        self.main_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.rules_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.records_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.main_layout)

    def start_game(self):
        # Останавливаем музыку перед запуском игры
        global global_media_player
        if global_media_player:
            global_media_player.stop()

        # Создаем экземпляр игры
        self.game_window = HanoiTowersGame()
        self.game_window.show()  # Показываем окно игры
        self.close()  # Закрываем текущее окно (главное меню)

    def show_rules(self):
        dialog = RulesDialog()
        dialog.exec()  # Открываем диалоговое окно с правилами

    def show_records(self):
        dialog = RecordsDialog()
        dialog.exec()  # Открываем диалоговое окно с рекордами

    def resizeEvent(self, event):
        # Переопределяем метод resizeEvent для изменения размера кнопок
        super().resizeEvent(event)

        # Вычисляем новый размер кнопок на основе размера окна
        new_width = self.width() // 4  
        self.play_button.setFixedWidth(new_width)
        self.rules_button.setFixedWidth(new_width)
        self.records_button.setFixedWidth(new_width)
        self.exit_button.setFixedWidth(new_width)

    def closeEvent(self, event):
        # Останавливаем музыку при закрытии приложения
        global global_media_player
        if global_media_player:
            global_media_player.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())