
import psutil
import sqlite3


from PyQt5.QtCore import  QThread, pyqtSignal


class DatabaseThread(QThread):
    timer_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = False
        self.start_time = 0

    def start_recording(self):
        self.running = True
        self.start_time = 0

    def stop_recording(self):
        self.running = False

    def run(self):
        # Подключение к базе данных создаётся в потоке
        connection = sqlite3.connect("system_data.db")
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS system_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu_load REAL,
            ram_load REAL,
            disk_usage REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        connection.commit()

        while self.running:
            # Сбор данных системы
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            # Запись данных в базу
            cursor.execute(
                "INSERT INTO system_stats (cpu_load, ram_load, disk_usage) VALUES (?, ?, ?)",
                (cpu, ram, disk)
            )
            connection.commit()

            # Отправляем сигнал с таймером записи
            self.start_time += 1
            self.timer_signal.emit(self.start_time)
            self.sleep(1)

        # Закрытие соединения с базой данных
        connection.close()