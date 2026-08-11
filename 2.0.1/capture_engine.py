# capture_engine.py
import os
import sys
import json
import time
import logging
import cv2
import numpy as np
import winreg                                  # 注册表操作
from PyQt5.QtCore import QObject, QThread
from capture_worker import CaptureWorker
from camera_utils import find_best_resolution
from config import CONFIG_FILE

class CaptureEngine(QObject):
    def __init__(self):
        super().__init__()
        self.config = self.default_config()
        self.worker = None
        self.thread = None
        self.auto_start = False
        self.load_config()
        idx = self.config.get("camera_index", 0)
        w, h = find_best_resolution(idx)
        self.config["best_width"] = w
        self.config["best_height"] = h
        self.save_config()

    def default_config(self):
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        default_root = os.path.join(base_dir, "timelapsephotos")
        return {
            "camera_index": 0,
            "root_directory": default_root,
            "interval_seconds": 3600,
            "use_png": True,
            "stack_enabled": True,
            "stack_count": 4,
            "stack_frame_interval": 0.1,
            "threshold_brightness": 0.08,
            "threshold_color": 0.10,
            "threshold_change_rate": 0.15,
            "ema_alpha": 0.05,
            "ema_protect_threshold": 0.30,
            "baseline_min_brightness": 50,
            "baseline_max_brightness": 200,
            "baseline_retry_limit": 3,
            "consecutive_severe_limit": 3,
            "dynamic_alpha_high": 0.3,
            "dynamic_protect_high": 0.6,
            "capture_retry_count": 5,
            "capture_retry_delay": 10,
            "autostart": False,
            "auto_start_capture": False,
            "best_width": 1920,
            "best_height": 1080,
            "ema_baseline": None,
            "exposure_manual": False,
            "exposure_value": -6.0,
            "frame_retry_count": 3
        }

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                self.config.update(loaded)
                logging.info("配置已加载")
            except Exception as e:
                logging.error(f"配置加载失败: {e}")
        self.auto_start = self.config.get("auto_start_capture", False)
        self.sync_autostart()

    def update_config(self, new_cfg):
        self.config.update(new_cfg)
        idx = self.config.get("camera_index", 0)
        w, h = find_best_resolution(idx)
        self.config["best_width"] = w
        self.config["best_height"] = h
        self.save_config()
        was_running = self.worker and self.worker._running
        self.stop_capture()
        if was_running or self.config.get("auto_start_capture"):
            self.start_capture()

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info("配置已保存")
        except Exception as e:
            logging.error(f"配置保存失败: {e}")

    def start_capture(self):
        if self.thread and self.thread.isRunning():
            return
        self.stop_capture()
        self.thread = QThread()
        self.worker = CaptureWorker(self.config)
        self.worker.moveToThread(self.thread)
        self.worker.status_update.connect(self.on_status_update)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        logging.info("拍摄已启动")

    def stop_capture(self):
        if self.worker:
            self.worker.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait(3000)
            self.thread = None
            self.worker = None
            logging.info("拍摄已停止")

    def manual_capture(self):
        temp_worker = CaptureWorker(self.config)
        return temp_worker.capture_one()

    def test_exposure(self):
        idx = self.config.get("camera_index", 0)
        root = self.config.get("root_directory", ".")
        w = self.config.get("best_width", 1920)
        h = self.config.get("best_height", 1080)
        manual = self.config.get("exposure_manual", False)
        exp_val = self.config.get("exposure_value", -6.0)

        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if not cap.isOpened():
            return False, "无法打开摄像头"
        if manual:
            try:
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                cap.set(cv2.CAP_PROP_EXPOSURE, exp_val)
            except Exception as e:
                cap.release()
                return False, f"应用曝光设置失败: {e}"
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        for _ in range(5):
            cap.read()
        time.sleep(0.3)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return False, "读取画面失败"
        os.makedirs(root, exist_ok=True)
        test_path = os.path.join(root, "exposure_test.jpg")
        cv2.imwrite(test_path, frame)
        avg_bright = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)[:, :, 2])
        info = (f"手动曝光{'已开启' if manual else '已关闭'}，设定值: {exp_val}\n"
                f"测试照片保存至: {test_path}\n"
                f"画面平均亮度: {avg_bright:.1f}")
        return True, info

    def on_status_update(self, msg):
        logging.info(f"状态: {msg}")

    # ---------- 开机自启（注册表实现）----------
    def set_autostart(self, enable):
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TimeLapseCapture"

        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            cmd_line = f'"{exe_path}" --autostart'
        else:
            python_exe = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            cmd_line = f'"{python_exe}" "{script_path}" --autostart'

        if enable:
            try:
                with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, cmd_line)
                logging.info("开机自启已设置（注册表）")
            except Exception as e:
                logging.error(f"设置开机自启失败: {e}")
        else:
            try:
                with winreg.OpenKey(key, sub_key, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.DeleteValue(reg_key, app_name)
                logging.info("开机自启已取消")
            except FileNotFoundError:
                pass
            except Exception as e:
                logging.error(f"取消开机自启失败: {e}")

    def sync_autostart(self):
        key = winreg.HKEY_CURRENT_USER
        sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TimeLapseCapture"
        exists = False
        try:
            with winreg.OpenKey(key, sub_key, 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, app_name)
            exists = True
        except FileNotFoundError:
            pass
        except Exception:
            pass
        if self.config.get("autostart") != exists:
            self.config["autostart"] = exists
            self.save_config()