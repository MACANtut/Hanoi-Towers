import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox,
    QHBoxLayout, QLabel, QDialog, QDialogButtonBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QUrl, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QIcon, QLinearGradient, QPalette, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class HanoiTowersGame(QWidget):
    return_to_menu = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('pictures/icon.ico'))
        self.num_disks = 3
        self.level = 1
        self.max_levels = 5
        self.pegs = [[], [], []]
        self.selected_disk = None
        self.selected_peg = None
        self.move_count = 0
        self.time_elapsed = 0
        self.records = self.load_records()
        self.mouse_pos = QPoint()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.music_enabled = True
        self.completed_levels = set()
        self.base_font_size = 12
        
        self.set_gradient_background()
        self.init_audio()
        self.initUI()

    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        self.setPalette(palette)

    def init_audio(self):
        self.background_player = QMediaPlayer()
        self.background_audio = QAudioOutput()
        self.background_player.setAudioOutput(self.background_audio)
        self.background_player.setSource(QUrl.fromLocalFile("sound/music.mp3"))
        self.background_audio.setVolume(0.3)
        self.background_player.setLoops(-1)
        if self.music_enabled:
            self.background_player.play()
        
        self.click_player = QMediaPlayer()
        self.click_audio = QAudioOutput()
        self.click_player.setAudioOutput(self.click_audio)
        self.click_player.setSource(QUrl.fromLocalFile("sound/click.mp3"))
        self.click_audio.setVolume(0.5)
        
        self.win_player = QMediaPlayer()
        self.win_audio = QAudioOutput()
        self.win_player.setAudioOutput(self.win_audio)
        self.win_player.setSource(QUrl.fromLocalFile("sound/win.mp3"))
        self.win_audio.setVolume(0.5)

    def load_records(self):
        try:
            with open('records.json', 'r') as f:
                records = json.load(f)
                for level, data in records.items():
                    if not isinstance(data, dict):
                        records[level] = {"time": data}
                return records
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_records(self):
        with open('records.json', 'w') as f:
            json.dump(self.records, f, indent=4)

    def update_record(self):
        current_record = self.records.get(str(self.level), {}).get('time', float('inf'))
        if self.time_elapsed < current_record:
            self.records[str(self.level)] = {"time": self.time_elapsed}
            self.save_records()
            self.update_timer_display()

    def initUI(self):
        self.setWindowTitle("Ханойские башни")

        main_layout = QVBoxLayout()
        
        button_style = """
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
            QPushButton:disabled {
                background: #483D8B;
                color: #A9A9A9;
            }
        """
        
        self.music_button = QPushButton(self)
        self.music_button.setIcon(QIcon.fromTheme("audio-volume-high"))
        self.music_button.setToolTip("Включить/выключить музыку")
        self.music_button.setFixedSize(80, 80)
        self.music_button.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.3);
                border: none;
                border-radius: 40px;
            }
            QPushButton:hover {
                background: rgba(106, 90, 205, 0.5);
            }
        """)
        self.music_button.clicked.connect(self.toggle_music)
        self.music_button.move(self.width() - 80, 10)

        self.menu_button = QPushButton("В меню", self)
        self.menu_button.setStyleSheet(button_style)
        self.menu_button.clicked.connect(self.show_exit_dialog)

        self.new_game_button = QPushButton("Новая игра", self)
        self.new_game_button.setStyleSheet(button_style)
        self.new_game_button.clicked.connect(self.new_game)

        self.next_level_button = QPushButton("Следующий уровень", self)
        self.next_level_button.setStyleSheet(button_style)
        self.next_level_button.clicked.connect(self.next_level)
        self.next_level_button.setEnabled(False)

        self.previous_level_button = QPushButton("Предыдущий уровень", self)
        self.previous_level_button.setStyleSheet(button_style)
        self.previous_level_button.clicked.connect(self.previous_level)
        self.previous_level_button.setEnabled(self.level > 1)

        self.level_label = QLabel(f"Уровень: {self.level}", self)
        self.level_label.setStyleSheet("color: white;")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.menu_button)
        button_layout.addWidget(self.new_game_button)
        button_layout.addWidget(self.previous_level_button)
        button_layout.addWidget(self.next_level_button)
        button_layout.addWidget(self.level_label)

        time_layout = QVBoxLayout()
        self.time_label = QLabel("Время выполнения: 00:00", self)
        self.time_label.setStyleSheet("color: white;")
        self.record_label = QLabel("Рекорд: --:--", self)
        self.record_label.setStyleSheet("color: white;")
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.record_label)
        time_layout.setSpacing(5)

        main_layout.addStretch(1)
        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.update_font_sizes()
        self.new_game()

    def update_font_sizes(self):
        font_multiplier = min(self.width(), self.height()) / 800
        
        button_font = QFont()
        button_font.setPointSize(int(self.base_font_size * font_multiplier))
        
        for button in [self.menu_button, self.new_game_button, 
                      self.next_level_button, self.previous_level_button]:
            button.setFont(button_font)
        
        label_font = QFont()
        label_font.setPointSize(int(self.base_font_size * font_multiplier))
        
        for label in [self.level_label, self.time_label, self.record_label]:
            label.setFont(label_font)

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.background_player.play()
            self.music_button.setIcon(QIcon.fromTheme("audio-volume-high"))
        else:
            self.background_player.pause()
            self.music_button.setIcon(QIcon.fromTheme("audio-volume-muted"))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.music_button.move(self.width() - 80, 10)
        self.set_gradient_background()
        self.update_font_sizes()

    def show_exit_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowIcon(QIcon('pictures/icon.ico'))
        dialog.setWindowTitle("Подтверждение выхода")
        dialog.setGeometry(200, 200, 300, 150)
        
        gradient = QLinearGradient(0, 0, dialog.width(), dialog.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        palette = dialog.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        dialog.setPalette(palette)

        layout = QVBoxLayout()
        message = QLabel("Вы точно хотите выйти в меню? Текущий прогресс не сохранится.", dialog)
        message.setStyleSheet("color: white;")
        layout.addWidget(message)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No, dialog)
        button_box.button(QDialogButtonBox.StandardButton.Yes).setText("Да")
        button_box.button(QDialogButtonBox.StandardButton.No).setText("Нет")
        button_box.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)

        button_box.accepted.connect(lambda: self.exit_to_menu(dialog))
        button_box.rejected.connect(dialog.close)

        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.exec()

    def exit_to_menu(self, dialog):
        self.background_player.stop()
        dialog.close()
        if hasattr(self, 'main_window'):
            self.main_window.last_geometry = self.geometry()
        self.return_to_menu.emit()
        self.close()

    def new_game(self):
        self.pegs = [[], [], []]
        for i in range(self.num_disks, 0, -1):
            self.pegs[0].append(i)
        self.move_count = 0
        self.time_elapsed = 0
        self.update_timer_display()
        self.timer.start(1000)
        self.update()
        self.update_level_buttons_state()

    def next_level(self):
        if self.level < self.max_levels:
            self.level += 1
            self.num_disks += 1
            self.level_label.setText(f"Уровень: {self.level}")
            self.new_game()
        else:
            QMessageBox.information(self, "Поздравляем!", "Вы прошли все уровни!")

        self.update_level_buttons_state()

    def previous_level(self):
        if self.level > 1:
            self.level -= 1
            self.num_disks -= 1
            self.level_label.setText(f"Уровень: {self.level}")
            self.new_game()
        self.update_level_buttons_state()

    def update_level_buttons_state(self):
        self.next_level_button.setEnabled(self.level in self.completed_levels and self.level < self.max_levels)
        self.previous_level_button.setEnabled(self.level > 1)

    def update_timer(self):
        self.time_elapsed += 1
        self.update_timer_display()

    def update_timer_display(self):
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.time_label.setText(f"Время выполнения: {minutes:02}:{seconds:02}")

        record = self.records.get(str(self.level), {}).get('time', None)
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
            QColor(255, 128, 0),
            QColor(0, 255, 0),
            QColor(0, 227, 255),
            QColor(0, 255, 112),
            QColor(255, 255, 255),
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

                color = colors[disk_size % len(colors)]
                if peg_index == self.selected_peg and disk_size == self.selected_disk:
                    color.setAlpha(128)
                
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
                self.click_player.play()

                if self.check_win():
                    self.timer.stop()
                    self.win_player.play()
                    self.completed_levels.add(self.level)
                    self.update_record()
                    if self.level == self.max_levels:
                        self.show_winner_dialog()
                    else:
                        self.show_win_message()

    def show_win_message(self):
        dialog = QDialog(self)
        dialog.setWindowIcon(QIcon('pictures/icon.ico'))
        dialog.setWindowTitle("Победа!")
        dialog.setGeometry(200, 200, 300, 150)
        
        gradient = QLinearGradient(0, 0, dialog.width(), dialog.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        palette = dialog.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        dialog.setPalette(palette)

        layout = QVBoxLayout()
        message = QLabel(f"Вы выиграли за {self.move_count} ходов!", dialog)
        message.setStyleSheet("color: white;")
        layout.addWidget(message)

        ok_button = QPushButton("OK", dialog)
        ok_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.setLayout(layout)
        dialog.exec()
        self.update_level_buttons_state()

    def show_winner_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowIcon(QIcon('pictures/icon.ico'))
        dialog.setWindowTitle("Поздравляем!")
        dialog.setGeometry(200, 200, 300, 150)
        
        gradient = QLinearGradient(0, 0, dialog.width(), dialog.height())
        gradient.setColorAt(0, QColor(75, 0, 130))
        gradient.setColorAt(1, QColor(25, 25, 112))
        palette = dialog.palette()
        palette.setBrush(QPalette.ColorRole.Window, gradient)
        dialog.setPalette(palette)

        layout = QVBoxLayout()
        message = QLabel("Вы прошли все уровни!", dialog)
        message.setStyleSheet("color: white;")
        layout.addWidget(message)

        new_game_button = QPushButton("Новая игра", dialog)
        new_game_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)
        new_game_button.clicked.connect(lambda: self.reset_game(dialog))
        layout.addWidget(new_game_button)

        quit_button = QPushButton("Выход", dialog)
        quit_button.setStyleSheet("""
            QPushButton {
                background: #6A5ACD;
                color: white;
                border: 1px solid #483D8B;
                padding: 5px;
            }
            QPushButton:hover {
                background: #7B68EE;
            }
        """)
        quit_button.clicked.connect(self.close)
        layout.addWidget(quit_button)

        dialog.setLayout(layout)
        dialog.exec()

    def reset_game(self, dialog):
        dialog.close()
        self.level = 1
        self.num_disks = 3
        self.level_label.setText(f"Уровень: {self.level}")
        self.new_game()
        self.completed_levels = set()
        self.update_level_buttons_state()

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
        return len(self.pegs[2]) == self.num_disks

class RulesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('pictures/icon.ico'))
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
        self.setWindowIcon(QIcon('pictures/icon.ico'))
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
        self.setWindowIcon(QIcon('pictures/icon.ico'))
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
        self.game_window.setGeometry(self.geometry())
        self.hide()
        self.game_window.show()

    def return_to_menu(self):
        self.last_geometry = self.game_window.geometry()
        self.game_window.close()
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