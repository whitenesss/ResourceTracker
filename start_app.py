import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")