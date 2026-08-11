# main.py
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSharedMemory
from config import LOG_FILE
from capture_engine import CaptureEngine
from system_tray import SystemTray

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    shared = QSharedMemory("TimeLapseCaptureApp")
    if not shared.create(1):
        print("程序已在运行。")
        sys.exit(1)

    engine = CaptureEngine()
    tray = SystemTray(engine)
    tray.show()

    if engine.config.get("auto_start_capture"):
        engine.start_capture()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()