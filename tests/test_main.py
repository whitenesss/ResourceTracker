import sqlite3
from main import MainWindow, HistoryWindow
from PyQt5.QtCore import QCoreApplication
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def main_window(qtbot):
    """Фикстура для создания экземпляра окна"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    return window

@pytest.fixture
def history_window(qtbot):
    """Фикстура для создания экземпляра окна HistoryWindow"""
    window = HistoryWindow()
    qtbot.addWidget(window)
    window.show()
    return window

def test_update_stats(main_window):
    """Проверяем обновление статистики"""
    with patch('psutil.cpu_percent', return_value=50), \
            patch('psutil.virtual_memory', return_value=MagicMock(percent=60)), \
            patch('psutil.disk_usage', return_value=MagicMock(percent=70)):
        main_window.update_stats()

        assert main_window.cpu_label.text() == "CPU: 50%"
        assert main_window.ram_label.text() == "RAM: 60%"
        assert main_window.disk_label.text() == "Disk: 70%"



def test_open_history_combined(main_window, qtbot):
    """Проверяем открытие окна истории и его отображение"""
    with patch('main.HistoryWindow') as MockHistoryWindow:
        mock_window = MockHistoryWindow.return_value
        mock_window.isVisible.return_value = True
        main_window.history_button.click()
        mock_window.exec.assert_called_once()

        qtbot.waitUntil(lambda: mock_window.isVisible(), timeout=1000)

        assert mock_window.isVisible(), "History window should be visible"




def test_error_handling_in_db(main_window):
    """Проверка обработки ошибок базы данных"""
    with patch.object(main_window.db_writer, 'start_recording', side_effect=sqlite3.DatabaseError("Database error")):
        main_window.start_recording()
        error_text = main_window.timer_label.text()
        print(f"Error text: {error_text}")
        assert "Error" in error_text, f"Expected error message in timer label, got: {error_text}"


def test_recording_time_update(main_window):
    """Проверяем обновление времени записи"""
    main_window.start_recording()
    QCoreApplication.processEvents()
    assert "Recording time:" in main_window.timer_label.text()





def test_spinbox_value_range(main_window):
    """Проверяем правильность диапазона и установку значений в QSpinBox"""
    main_window.interval_spinbox.setValue(5)
    assert main_window.interval_spinbox.value() == 5
    assert main_window.interval_spinbox.minimum() == 1
    assert main_window.interval_spinbox.maximum() == 10


def test_buttons_visibility_on_stop(main_window):
    """Проверяем видимость кнопок после остановки записи"""
    main_window.stop_recording()
    assert main_window.start_button.isVisible()
    assert not main_window.stop_button.isVisible()



def test_empty_data_load(history_window):
    """Проверка загрузки пустых данных в таблицу"""

    with patch("sqlite3.connect") as mock_connect:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_cursor.fetchall.return_value = []
        history_window.load_data()
        assert history_window.table.rowCount() == 0


def test_update_timer(main_window):
    """Проверка работы метода update_timer"""
    seconds = 120
    main_window.update_timer(seconds)
    assert main_window.timer_label.text() == f"Recording time: {seconds}s"
