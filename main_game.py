import sys
import json
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QUrl
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

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
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

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
        layout.addWidget(menu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

class HanoiTowersGame(QWidget):
    def __init__(self):
        super().__init__()
        self.num_disks = 3  # Начальное количество дисков
        self.level = 1  # Текущий уровень
        self.max_levels = 5  # Максимальное количество уровней
        self.pegs = [[], [], []]  # Три стержня
        self.selected_disk = None  # Выбранный диск для перемещения
        self.selected_peg = None  # Стержень, с которого выбран диск
        self.move_count = 0  # Счётчик ходов
        self.time_elapsed = 0  # Время выполнения (в секундах)
        self.records = self.load_records()  # Загружаем рекорды из файла
        self.mouse_pos = QPoint()  # Позиция курсора

        self.timer = QTimer(self)  # Таймер для отслеживания времени
        self.timer.timeout.connect(self.update_timer)

        # Инициализация медиаплеера для звука победы
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(QUrl.fromLocalFile("sound/победа.mp3"))

        # Инициализация медиаплеера для звука щелчка
        self.click_player = QMediaPlayer(self)
        self.click_audio_output = QAudioOutput(self)
        self.click_player.setAudioOutput(self.click_audio_output)
        self.click_player.setSource(QUrl.fromLocalFile("sound/щелчок.mp3"))

        # Инициализация медиаплеера для фоновой музыки
        self.background_music_player = QMediaPlayer(self)
        self.background_music_output = QAudioOutput(self)
        self.background_music_player.setAudioOutput(self.background_music_output)
        self.background_music_player.setSource(QUrl.fromLocalFile("sound/музыка.mp3"))
        self.background_music_player.mediaStatusChanged.connect(self.loop_background_music)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Ханойские башни")
        self.setGeometry(100, 100, 800, 600)

        # Основной layout
        main_layout = QVBoxLayout()

        # Кнопка "В меню"
        self.menu_button = QPushButton("В меню", self)
        self.menu_button.clicked.connect(self.show_exit_dialog)

        # Кнопка "Новая игра"
        self.new_game_button = QPushButton("Новая игра", self)
        self.new_game_button.clicked.connect(self.new_game)

        # Кнопка "Следующий уровень"
        self.next_level_button = QPushButton("Следующий уровень", self)
        self.next_level_button.clicked.connect(self.next_level)

        # Кнопка "Предыдущий уровень"
        self.previous_level_button = QPushButton("Предыдущий уровень", self)
        self.previous_level_button.clicked.connect(self.previous_level)

        # Отображение текущего уровня
        self.level_label = QLabel(f"Уровень: {self.level}", self)

        # Layout для кнопок и метки уровня
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.menu_button)
        button_layout.addWidget(self.new_game_button)
        button_layout.addWidget(self.previous_level_button)
        button_layout.addWidget(self.next_level_button)
        button_layout.addWidget(self.level_label)

        main_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        # Время выполнения и рекорд
        self.time_label = QLabel("Время выполнения: 00:00", self)
        self.record_label = QLabel("Рекорд: --:--", self)

        # Layout для времени и рекорда
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.time_label)
        bottom_layout.addWidget(self.record_label)

        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)

        # Инициализация игры
        self.new_game()

        # Запуск фоновой музыки
        if self.background_music_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.background_music_player.stop()
        self.background_music_player.play()

    def show_exit_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Подтверждение выхода")
        dialog.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        message = QLabel("Вы точно хотите выйти в меню? Текущий прогресс не сохранится.", dialog)
        layout.addWidget(message)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No, dialog)
        button_box.button(QDialogButtonBox.StandardButton.Yes).setText("Да")
        button_box.button(QDialogButtonBox.StandardButton.No).setText("Нет")

        button_box.accepted.connect(lambda: self.exit_to_menu(dialog))
        button_box.rejected.connect(dialog.close)

        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def exit_to_menu(self, dialog):
        dialog.close()
        self.close()
        self.open_main_menu()

    def open_main_menu(self):
        self.main_window = MainWindow()
        self.main_window.show()

    def loop_background_music(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.background_music_player.setPosition(0)
            self.background_music_player.play()

    def new_game(self):
        self.pegs = [[], [], []]
        for i in range(self.num_disks, 0, -1):
            self.pegs[0].append(i)
        self.move_count = 0
        self.time_elapsed = 0
        self.update_timer_display()
        self.timer.start(1000)
        self.update()

        self.update_next_level_button_state()

    def next_level(self):
        if self.level < self.max_levels:
            self.level += 1
            self.num_disks += 1
            self.level_label.setText(f"Уровень: {self.level}")
            self.new_game()
        else:
            QMessageBox.information(self, "Поздравляем!", "Вы прошли все уровни!")

        self.update_next_level_button_state()

    def previous_level(self):
        if self.level > 1:
            self.level -= 1
            self.num_disks -= 1
            self.level_label.setText(f"Уровень: {self.level}")
            self.new_game()

        self.update_next_level_button_state()

    def update_next_level_button_state(self):
        if self.level == self.max_levels:
            self.next_level_button.setEnabled(False)
        else:
            self.next_level_button.setEnabled(True)

    def update_timer(self):
        self.time_elapsed += 1
        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.time_label.setText(f"Время выполнения: {minutes:02}:{seconds:02}")

        record = self.records.get(self.level, None)
        if record is not None:
            record_minutes = record // 60
            record_seconds = record % 60
            self.record_label.setText(f"Рекорд: {record_minutes:02}:{record_seconds:02}")
        else:
            self.record_label.setText("Рекорд: --:--")

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_pegs(painter)
        self.draw_disks(painter)

    def draw_pegs(self, painter):
        peg_width = 10
        peg_height = self.height() // 2
        peg_color = QColor(139, 69, 19)
        painter.setBrush(QBrush(peg_color))

        peg_spacing = self.width() // 4
        for i in range(3):
            x = peg_spacing + i * peg_spacing - peg_width // 2
            y = self.height() - peg_height
            painter.drawRect(x, y, peg_width, -peg_height)

    def draw_disks(self, painter):
        disk_height = 20
        colors = [
            QColor(255, 0, 0),
            QColor(0, 255, 0),
            QColor(0, 0, 255),
            QColor(255, 255, 0),
            QColor(255, 0, 255),
            QColor(0, 255, 255),
            QColor(128, 0, 128),
        ]

        peg_spacing = self.width() // 4
        peg_height = self.height() // 2

        for peg_index, peg in enumerate(self.pegs):
            x_base = peg_spacing + peg_index * peg_spacing
            for disk_index, disk_size in enumerate(peg):
                disk_width = 50 + disk_size * 20
                x = x_base - disk_width // 2
                y = self.height() - (disk_index + 1) * disk_height - (self.height() - peg_height)

                if peg_index == self.selected_peg and disk_size == self.selected_disk:
                    color = colors[disk_size % len(colors)]
                    color.setAlpha(128)
                else:
                    color = colors[disk_size % len(colors)]

                painter.setBrush(QBrush(color))
                painter.drawRect(x, y, disk_width, disk_height)

        if self.selected_disk is not None:
            disk_width = 50 + self.selected_disk * 20
            x = self.mouse_pos.x() - disk_width // 2
            y = self.mouse_pos.y() - disk_height // 2
            color = colors[self.selected_disk % len(colors)]
            color.setAlpha(128)
            painter.setBrush(QBrush(color))
            painter.drawRect(x, y, disk_width, disk_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            peg_index = self.get_peg_index(event.pos().x())
            if peg_index is not None and self.pegs[peg_index]:
                self.selected_disk = self.pegs[peg_index][-1]
                self.selected_peg = peg_index
                self.mouse_pos = event.pos()
                self.update()

    def mouseMoveEvent(self, event):
        if self.selected_disk is not None:
            self.mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selected_disk is not None:
            target_peg_index = self.get_peg_index(event.pos().x())
            if target_peg_index is not None and self.is_valid_move(target_peg_index):
                self.pegs[self.selected_peg].pop()
                self.pegs[target_peg_index].append(self.selected_disk)
                self.move_count += 1
                self.selected_disk = None
                self.selected_peg = None
                self.update()

                if not self.check_win():
                    if self.click_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                        self.click_player.stop()
                    self.click_player.play()

                if self.check_win():
                    self.timer.stop()
                    if self.level == self.max_levels:
                        self.show_winner_dialog()
                    else:
                        QMessageBox.information(self, "Победа!", f"Вы выиграли за {self.move_count} ходов!")
                        self.update_record()

    def show_winner_dialog(self):
        winner_dialog = QDialog(self)
        winner_dialog.setWindowTitle("Поздравляем!")
        winner_dialog.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout()

        message = QLabel("Вы прошли все уровни!", winner_dialog)
        layout.addWidget(message)

        new_game_button = QPushButton("Новая игра", winner_dialog)
        new_game_button.clicked.connect(lambda: self.reset_game(winner_dialog))
        layout.addWidget(new_game_button)

        quit_button = QPushButton("Выход", winner_dialog)
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        winner_dialog.setLayout(layout)
        winner_dialog.exec()

    def reset_game(self, dialog):
        dialog.close()
        self.level = 1
        self.num_disks = 3
        self.level_label.setText(f"Уровень: {self.level}")
        self.new_game()

    def update_record(self):
        current_record = self.records.get(self.level, float("inf"))
        if self.time_elapsed < current_record:
            self.records[self.level] = self.time_elapsed
            self.update_timer_display()

    def get_peg_index(self, x):
        peg_spacing = self.width() // 3
        for i in range(3):
            if i * peg_spacing < x < (i + 1) * peg_spacing:
                return i
        return None

    def is_valid_move(self, target_peg_index):
        if not self.pegs[target_peg_index]:
            return True
        return self.selected_disk < self.pegs[target_peg_index][-1]

    def check_win(self):
        if len(self.pegs[2]) == self.num_disks:
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.media_player.stop()
            self.media_player.play()
            return True
        return False

    def load_records(self):
        try:
            with open("records.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_records(self):
        with open("records.json", "w") as file:
            json.dump(self.records, file)

    def closeEvent(self, event):
        self.background_music_player.stop()
        self.media_player.stop()
        self.click_player.stop()
        self.save_records()
        event.accept()

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
        self.records_button.set