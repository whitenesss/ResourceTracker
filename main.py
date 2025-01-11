import sys
import psutil

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget, QSpinBox
from PyQt5.QtCore import QTimer
from db_manager import DatabaseThread




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor")
        self.setGeometry(100, 100, 800, 600)

        # Создание виджетов
        self.cpu_label = QLabel("CPU: 0%", self)
        self.ram_label = QLabel("RAM: 0%", self)
        self.disk_label = QLabel("Disk: 0%", self)
        self.timer_label = QLabel("Recording time: 0s", self)
        self.start_button = QPushButton("Start Recording", self)
        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.hide()

        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setSuffix(" s")
        self.interval_spinbox.setRange(1, 10)

        # Таймер для обновления метрик
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)

        # Объект для записи в базу данных
        self.db_writer = DatabaseThread()
        self.db_writer.timer_signal.connect(self.update_timer)

        # Макет
        layout = QVBoxLayout()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.interval_spinbox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключение сигналов кнопок
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

        # Запуск таймера
        self.timer.start(1000)

    def update_stats(self):
        """Обновление данных CPU, RAM и Disk."""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram}%")
        self.disk_label.setText(f"Disk: {disk}%")

    def start_recording(self):
        """Начало записи в базу данных."""
        self.start_button.hide()
        self.stop_button.show()
        self.db_writer.start_recording()
        self.db_writer.start()

    def stop_recording(self):
        """Остановка записи в базу данных."""
        self.start_button.show()
        self.stop_button.hide()
        self.db_writer.stop_recording()
        self.timer_label.setText("Recording time: 0s")

    def update_timer(self, seconds):
        """Обновление времени записи."""
        self.timer_label.setText(f"Recording time: {seconds}s")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
