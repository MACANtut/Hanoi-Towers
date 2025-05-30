import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QDialog, QScrollArea, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class RulesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Правила игры")
        self.setGeometry(100, 100, 600, 300)

        rules_text = """Правила игры "Ханойские башни":
1. Начальная позиция: все диски располагаются на одном из стержней (обычно на левом) в порядке убывания размера, 
то есть самый большой диск внизу, а самый маленький — сверху;
2. Перемещение дисков: игрок может перемещать только один диск за раз. 
Диск можно взять с верхней части стержня и переместить его на другой стержень. 
Перемещать диски можно, зажав определённый диск и перенести его на новую позицию, а также нажав на необходимый диск, а затем нажать на новое место;
3. Запрет на размещение: никогда нельзя помещать больший диск на меньший. 
Диски должны всегда располагаться в порядке убывания размера;
4. Цель перемещения: игрок должен переместить все диски на другой стержень за минимальное количество времени (обычно на правый).
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
        self.setGeometry(100, 100, 400, 300)

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

        # Создание layout для кнопок в правом углу
        corner_layout = QHBoxLayout()
        corner_layout.addStretch()  # Добавляем растяжку, чтобы кнопки были справа

        # Создание квадратных кнопок
        self.corner_button1 = QPushButton()
        self.corner_button2 = QPushButton()

        # Установка фиксированного размера для кнопок (квадратные)
        button_size = 50  # Размер кнопок
        self.corner_button1.setFixedSize(button_size, button_size)
        self.corner_button2.setFixedSize(button_size, button_size)

        # Подключение действий к кнопкам
        self.corner_button1.clicked.connect(self.on_corner_button1_clicked)
        self.corner_button2.clicked.connect(self.on_corner_button2_clicked)

        # Добавление кнопок в правый угол
        corner_layout.addWidget(self.corner_button1)
        corner_layout.addWidget(self.corner_button2)

        # Добавление corner_layout в основной layout
        self.main_layout.addLayout(corner_layout)

        self.setLayout(self.main_layout)

    def start_game(self):
        # Здесь можно добавить логику для начала игры
        print("Игра начата!")

    def show_rules(self):
        dialog = RulesDialog()
        dialog.exec()  # В PyQt6 используется exec() вместо exec_()

    def show_records(self):
        dialog = RecordsDialog()
        dialog.exec()  # В PyQt6 используется exec() вместо exec_()

    def on_corner_button1_clicked(self):
        # Действие для первой кнопки
        print("Кнопка 1 нажата!")
        # Загрузка изображения на кнопку
        self.corner_button1.setIcon(QIcon(""))  # Укажите путь к изображению
        self.corner_button1.setIconSize(self.corner_button1.size())

    def on_corner_button2_clicked(self):
        # Действие для второй кнопки
        print("Кнопка 2 нажата!")
        # Загрузка изображения на кнопку
        self.corner_button2.setIcon(QIcon(""))  # Укажите путь к изображению
        self.corner_button2.setIconSize(self.corner_button2.size())

    def resizeEvent(self, event):
        # Переопределяем метод resizeEvent для изменения размера кнопок
        super().resizeEvent(event)

        # Вычисляем новый размер кнопок на основе размера окна
        new_width = self.width() // 4  # Пример: ширина кнопок зависит от ширины окна
        self.play_button.setFixedWidth(new_width)
        self.rules_button.setFixedWidth(new_width)
        self.records_button.setFixedWidth(new_width)
        self.exit_button.setFixedWidth(new_width)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())