
import psutil
import sqlite3
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import (
 QMainWindow, QVBoxLayout, QPushButton, QLabel, QWidget,
    QSpinBox, QTableWidget, QTableWidgetItem, QDialog
)
from PyQt5.QtCore import QTimer
from db_manager import DatabaseThread


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("History of Records")
        self.setGeometry(200, 200, 600, 400)

        # Таблица для отображения данных
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "CPU Load (%)", "RAM Load (%)", "Disk Usage (%)", "Timestamp"])

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        # Подключаемся к базе данных и считываем записи
        connection = sqlite3.connect("system_data.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM system_stats")
        records = cursor.fetchall()
        connection.close()

        # Добавляем записи в таблицу
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor")
        self.setGeometry(100, 100, 800, 600)

        # Виджеты
        self.cpu_label = QLabel("CPU: 0%", self)
        self.ram_label = QLabel("RAM: 0%", self)
        self.disk_label = QLabel("Disk: 0%", self)
        self.timer_label = QLabel("Recording time: 0s", self)

        self.start_button = QPushButton("Start Recording", self)
        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.hide()
        self.history_button = QPushButton("View History", self)

        self.interval_spinbox = QSpinBox(self)
        self.interval_spinbox.setValue(1)
        self.interval_spinbox.setSuffix(" s")
        self.interval_spinbox.setRange(1, 10)

        # Таймер для обновления данных на экране
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)

        # Поток для работы с базой данных
        self.db_writer = DatabaseThread()
        self.db_writer.timer_signal.connect(self.update_timer)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(QLabel("Update and record interval:"))
        layout.addWidget(self.interval_spinbox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.history_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Сигналы кнопок
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.interval_spinbox.valueChanged.connect(self.update_interval)
        self.history_button.clicked.connect(self.open_history)

        # Запуск таймера обновления данных
        self.timer.start(1000)

    def update_stats(self):
        """Обновление статистики ЦП, ОЗУ и ПЗУ на экране"""
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram}%")
        self.disk_label.setText(f"Disk: {disk}%")

    def update_interval(self):
        """Обновление интервала записи данных и обновления экрана"""
        interval = self.interval_spinbox.value()
        self.timer.setInterval(interval * 1000)
        self.db_writer.set_interval(interval)

    def start_recording(self):
        """Начало записи данных в базу"""
        print("Start recording called!")

        self.start_button.hide()
        print(f"Start button hidden: {not self.start_button.isVisible()}")

        self.stop_button.show()
        print(f"Stop button shown: {self.stop_button.isVisible()}")

        try:
            # Попытка начать запись
            self.db_writer.start_recording()
            self.db_writer.start()
            print("Recording started successfully!")
        except sqlite3.DatabaseError as e:
            # Обработка ошибки базы данных
            error_message = f"Error: {str(e)}"
            self.timer_label.setText(error_message)  # Устанавливаем текст ошибки на метке
            print(f"Database error: {e}")

            # Логирование ошибки
            import traceback
            print("Detailed error info:", traceback.format_exc())

            return  # Прерывание выполнения функции при ошибке

        QCoreApplication.processEvents()  # Обработка событий интерфейса
        print(f"Stop button visible after events: {self.stop_button.isVisible()}")

    def stop_recording(self):
        """Остановка записи данных в базу"""
        self.start_button.show()
        self.stop_button.hide()
        self.db_writer.stop_recording()
        self.timer_label.setText("Recording time: 0s")

    def update_timer(self, seconds):
        """Обновление таймера записи на экране"""
        self.timer_label.setText(f"Recording time: {seconds}s")

    def open_history(self):
        # Открываем окно истории
        self.history_window = HistoryWindow()
        self.history_window.exec()

    def closeEvent(self, event):
        """Закрытие приложения"""
        self.db_writer.stop_recording()
        self.db_writer.quit()
        self.db_writer.wait()
        event.accept()


