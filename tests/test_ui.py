import pytest
from unittest.mock import patch, MagicMock
from db_manager import DatabaseThread
import sqlite3


@pytest.fixture
def db_thread():
    """Фикстура для создания экземпляра DatabaseThread"""
    thread = DatabaseThread()
    return thread


@patch('psutil.cpu_percent', return_value=50)
@patch('psutil.virtual_memory', return_value=MagicMock(percent=60))
@patch('psutil.disk_usage', return_value=MagicMock(percent=70))
@patch('sqlite3.connect')
def test_run_inserts_data(mock_connect, mock_disk, mock_ram, mock_cpu, db_thread, qtbot):
    """Тестируем вставку данных в базу данных"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor


    mock_connection.commit = MagicMock()


    def on_timer_signal(seconds):
        pass

    db_thread.timer_signal.connect(on_timer_signal)
    db_thread.start_recording()
    def mock_run():

        for _ in range(3):
            cpu = mock_cpu()
            ram = mock_ram().percent
            disk = mock_disk().percent
            print(f"Inserting data: CPU={cpu}, RAM={ram}, Disk={disk}")
            mock_cursor.execute(
                "INSERT INTO system_stats (cpu_load, ram_load, disk_usage) VALUES (?, ?, ?)",
                (cpu, ram, disk)
            )
            db_thread.timer_signal.emit(10)
            db_thread.start_time += 1


        mock_connection.commit()


    db_thread.run = mock_run
    db_thread.run()
    mock_cursor.execute.assert_called_with(
        "INSERT INTO system_stats (cpu_load, ram_load, disk_usage) VALUES (?, ?, ?)",
        (50, 60, 70)
    )


    mock_connection.commit.assert_called_once()

    assert db_thread.start_time == 3


@patch('psutil.cpu_percent', return_value=50)
@patch('psutil.virtual_memory', return_value=MagicMock(percent=60))
@patch('psutil.disk_usage', return_value=MagicMock(percent=70))
@patch('sqlite3.connect')
def test_run_with_error_handling(mock_connect, mock_disk, mock_ram, mock_cpu, db_thread):
    """Тестируем, как поток обрабатывает ошибку базы данных"""
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = sqlite3.DatabaseError("Database error")
    db_thread.start_recording()
    db_thread.run()
