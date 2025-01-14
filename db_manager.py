import psutil
import sqlite3
from PyQt5.QtCore import QThread, pyqtSignal
import time

class DatabaseThread(QThread):
    timer_signal = pyqtSignal(int)
    data_inserted = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = False
        self.interval = 1  # Интервал записи данных по умолчанию (в секундах)
        self.connection = None
        self.cursor = None
        self.start_time = 0

    def set_interval(self, interval):
        """Установить интервал записи данных"""
        self.interval = interval

    def start_recording(self):
        self.running = True
        self.start_time = 0

    def stop_recording(self):
        self.running = False

    def run(self):
        try:
            # Подключение к базе данных (создаётся в отдельном потоке)
            self.connection = sqlite3.connect("system_data.db")
            self.cursor = self.connection.cursor()
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpu_load REAL,
                ram_load REAL,
                disk_usage REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
            self.connection.commit()
            print("Database connection established.")
            # Основной цикл записи данных в базу
            while self.running:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                print(f"Inserting data: CPU={cpu}, RAM={ram}, Disk={disk}")
                self.cursor.execute(
                    "INSERT INTO system_stats (cpu_load, ram_load, disk_usage) VALUES (?, ?, ?)",
                    (cpu, ram, disk)
                )
                self.data_inserted.emit(cpu)
                self.connection.commit()


                self.start_time += self.interval
                self.timer_signal.emit(self.start_time)
                self.sleep(self.interval)

        except sqlite3.Error as e:
            print(f"Database error: {e}")

        finally:
            if self.connection:
                self.connection.close()

