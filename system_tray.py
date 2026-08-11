# system_tray.py
import os
import sys
from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QApplication, QStyle
)
from PyQt5.QtGui import QIcon
from settings_dialog import SettingsDialog


def get_icon_path():
    """获取图标文件路径，兼容开发和打包环境"""
    if getattr(sys, 'frozen', False):
        # 打包后，图标文件在临时目录中
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "camera_icon.ico")


class SystemTray(QSystemTrayIcon):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

        # 尝试加载自定义图标
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # 回退：使用系统标准图标（保证托盘可见）
            self.setIcon(QApplication.style().standardIcon(QStyle.SP_ComputerIcon))

        self.setToolTip("延时摄影 - 高画质自适应")

        menu = QMenu()
        self.open_action = QAction("打开设置")
        self.open_action.triggered.connect(self.open_settings)
        menu.addAction(self.open_action)

        self.capture_action = QAction("立即拍摄一张")
        self.capture_action.triggered.connect(self.manual_capture)
        menu.addAction(self.capture_action)

        menu.addSeparator()
        self.quit_action = QAction("退出程序")
        self.quit_action.triggered.connect(self.quit_app)
        menu.addAction(self.quit_action)

        self.setContextMenu(menu)

    def open_settings(self):
        dlg = SettingsDialog(self.engine)
        dlg.exec_()

    def manual_capture(self):
        success = self.engine.manual_capture()
        if success:
            self.showMessage("拍摄成功", "已保存一张照片。", QSystemTrayIcon.Information, 2000)
        else:
            self.showMessage("拍摄失败", "请检查摄像头连接。", QSystemTrayIcon.Warning, 2000)

    def quit_app(self):
        self.engine.stop_capture()
        self.hide()
        QApplication.quit()