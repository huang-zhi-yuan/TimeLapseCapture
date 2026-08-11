# capture_worker.py
import os
import json
import time
import logging
import numpy as np
import cv2
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from camera_utils import create_default_baseline
from config import CONFIG_FILE

class CaptureWorker(QObject):
    finished = pyqtSignal()
    status_update = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._running = False
        self.ema_stats = self.config.get("ema_baseline", None)
        self.last_stats = None
        self.ema_alpha = self.config.get("ema_alpha", 0.05)
        self.protect_threshold = self.config.get("ema_protect_threshold", 0.30)
        self.severe_count = 0
        self.dynamic_mode = False
        self.baseline_fail_count = 0
        self.frame_retry_count = self.config.get("frame_retry_count", 3)

    def run(self):
        self._running = True
        interval = self.config.get("interval_seconds", 3600)
        while self._running:
            start = time.time()
            self.capture_one()
            if not self._running:
                break
            elapsed = time.time() - start
            sleep_time = max(0, interval - elapsed)
            while sleep_time > 0 and self._running:
                time.sleep(min(1, sleep_time))
                sleep_time -= 1
        self.finished.emit()

    def capture_one(self):
        idx = self.config.get("camera_index", 0)
        root = self.config.get("root_directory", ".")
        stack_enabled = self.config.get("stack_enabled", True)
        stack_count = self.config.get("stack_count", 4)

        now = datetime.now()
        date_path = os.path.join(root, str(now.year), f"{now.month:02d}", f"{now.day:02d}")
        os.makedirs(date_path, exist_ok=True)

        timestamp = now.strftime("%Y%m%d_%H%M%S")
        fullpath = os.path.join(date_path, f"img_{timestamp}.png")

        for attempt in range(self.frame_retry_count):
            frame = self.get_high_quality_frame(idx, stack_enabled, stack_count)
            if frame is None:
                logging.error("获取画面失败，放弃本次拍摄")
                self.status_update.emit("获取失败")
                return False
            if self._is_abnormal_dark(frame):
                logging.warning(f"检测到异常暗帧，重试 ({attempt+1}/{self.frame_retry_count})")
                time.sleep(0.5)
                continue
            corrected, msg = self.auto_detect_and_correct(frame)
            cv2.imwrite(fullpath, corrected)
            logging.info(f"保存: {fullpath} | {msg}")
            self.status_update.emit(f"拍摄: {timestamp} ({msg})")
            return True
        if frame is not None:
            corrected, msg = self.auto_detect_and_correct(frame)
            cv2.imwrite(fullpath, corrected)
            logging.warning(f"重试耗尽，保存可能异常帧: {fullpath}")
            self.status_update.emit(f"拍摄: {timestamp} (可能异常)")
            return True
        return False

    def _is_abnormal_dark(self, frame, threshold=5.0):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        return brightness < threshold

    def get_high_quality_frame(self, idx, stack_enabled, stack_count):
        max_retries = self.config.get("capture_retry_count", 5)
        retry_delay = self.config.get("capture_retry_delay", 10)
        w = self.config.get("best_width", 1920)
        h = self.config.get("best_height", 1080)
        for attempt in range(max_retries):
            frame = self._try_get_frame(idx, w, h, stack_enabled, stack_count)
            if frame is not None:
                return frame
            if attempt < max_retries - 1:
                logging.warning(f"摄像头被占用，{retry_delay}秒后重试({attempt+1}/{max_retries})")
                time.sleep(retry_delay)
        logging.error(f"重试{max_retries}次后仍无法获取画面")
        return None

    def _try_get_frame(self, idx, w, h, stack_enabled, stack_count):
        if stack_enabled and stack_count > 1:
            # 堆栈模式：保持摄像头常开，连续抓取多帧
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not cap.isOpened():
                return None
            self.apply_camera_settings(cap)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            # 预热
            for _ in range(5):
                cap.read()
            time.sleep(0.2)
            frames = []
            for i in range(stack_count):
                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.release()
                    return None
                frames.append(frame.astype(np.float32))
                if i < stack_count - 1:
                    # 可配置的帧间间隔（秒）
                    interval = self.config.get("stack_frame_interval", 0.1)
                    time.sleep(interval)
            cap.release()
            if frames:
                return np.mean(frames, axis=0).astype(np.uint8)
            return None
        else:
            # 单帧模式
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap.release()
                return None
            self.apply_camera_settings(cap)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            for _ in range(5):
                cap.read()
            time.sleep(0.2)
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                return frame
            return None

    def apply_camera_settings(self, cap):
        if self.config.get("exposure_manual", False):
            try:
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
                cap.set(cv2.CAP_PROP_EXPOSURE, self.config.get("exposure_value", -6))
            except Exception as e:
                logging.warning(f"设置手动曝光失败: {e}")

    def auto_detect_and_correct(self, frame):
        stats = self.compute_stats(frame)
        current_bright = stats["brightness"]

        # 基准建立
        if self.ema_stats is None:
            min_bright = self.config.get("baseline_min_brightness", 50)
            max_bright = self.config.get("baseline_max_brightness", 200)
            if current_bright < min_bright:
                self.baseline_fail_count += 1
                limit = self.config.get("baseline_retry_limit", 3)
                if self.baseline_fail_count >= limit:
                    self.ema_stats = create_default_baseline()
                    self.last_stats = self.ema_stats.copy()
                    self.config["ema_baseline"] = self.ema_stats
                    self.save_config_to_disk()
                    self.baseline_fail_count = 0
                    return frame, "已启用默认基准(过暗)"
                return frame, "基准未建立(过暗)"
            elif current_bright > max_bright:
                self.baseline_fail_count += 1
                limit = self.config.get("baseline_retry_limit", 3)
                if self.baseline_fail_count >= limit:
                    self.ema_stats = create_default_baseline()
                    self.last_stats = self.ema_stats.copy()
                    self.config["ema_baseline"] = self.ema_stats
                    self.save_config_to_disk()
                    self.baseline_fail_count = 0
                    return frame, "已启用默认基准(过亮)"
                return frame, "基准未建立(过亮)"
            else:
                self.ema_stats = stats
                self.last_stats = stats
                self.config["ema_baseline"] = stats
                self.save_config_to_disk()
                self.baseline_fail_count = 0
                logging.info(f"基准建立成功，平均亮度: {current_bright:.1f}")
                return frame, "基准已建立"

        # 异常暗帧保护
        if current_bright < 10 and self.ema_stats["brightness"] > 50:
            logging.warning("疑似硬件异常暗帧，跳过校正与基准更新")
            return frame, "异常暗帧(未处理)"

        thresh_bright = self.config.get("threshold_brightness", 0.08)
        thresh_color = self.config.get("threshold_color", 0.10)
        thresh_change = self.config.get("threshold_change_rate", 0.15)

        bright_dev = abs(stats["brightness"] - self.ema_stats["brightness"]) / max(self.ema_stats["brightness"], 1)
        color_dev = self._color_deviation(stats, self.ema_stats)
        change_rate = self._frame_change_rate(stats, self.last_stats)

        need_correct = False
        reason = ""
        if bright_dev > thresh_bright or color_dev > thresh_color:
            need_correct = True
            reason = f"偏离基准 (亮度:{bright_dev:.2%}, 色彩:{color_dev:.2%})"
        elif change_rate > thresh_change:
            need_correct = True
            reason = f"突变检测 (变化率:{change_rate:.2%})"

        if not need_correct:
            if self._is_anomaly(stats, self.ema_stats):
                logging.warning("异常帧跳过EMA更新（保护中）")
                self.last_stats = stats
                self._reset_severe_mode()
                return frame, "正常(异常帧跳过更新)"
            else:
                self._update_ema(stats)
                self.last_stats = stats
                self._reset_severe_mode()
                return frame, "正常"
        else:
            logging.warning(f"需修正: {reason}")
            corrected = self.apply_correction(frame, self.ema_stats, stats)
            new_stats = self.compute_stats(corrected)
            new_bright_dev = abs(new_stats["brightness"] - self.ema_stats["brightness"]) / max(self.ema_stats["brightness"], 1)
            new_color_dev = self._color_deviation(new_stats, self.ema_stats)
            if new_bright_dev < thresh_bright * 1.5 and new_color_dev < thresh_color * 1.5:
                self.last_stats = new_stats
                self._reset_severe_mode()
                return corrected, f"已修正 ({reason})"
            else:
                msg = "严重异常！修正后仍偏差较大，请检查环境/摄像头。"
                logging.error(msg)
                self.status_update.emit(msg)
                self.last_stats = new_stats
                self._handle_severe()
                return corrected, msg

    def _handle_severe(self):
        self.severe_count += 1
        limit = self.config.get("consecutive_severe_limit", 3)
        if self.severe_count >= limit and not self.dynamic_mode:
            self.dynamic_mode = True
            self.ema_alpha = self.config.get("dynamic_alpha_high", 0.3)
            self.protect_threshold = self.config.get("dynamic_protect_high", 0.6)
            logging.warning(f"连续{self.severe_count}次严重异常，进入动态适应模式")
            self.status_update.emit("进入动态适应模式")

    def _reset_severe_mode(self):
        if self.dynamic_mode:
            self.dynamic_mode = False
            self.ema_alpha = self.config.get("ema_alpha", 0.05)
            self.protect_threshold = self.config.get("ema_protect_threshold", 0.30)
            logging.info("严重异常已解除，恢复原始参数")
            self.status_update.emit("恢复常规参数")
        self.severe_count = 0

    def _is_anomaly(self, stats, baseline):
        bright_dev = abs(stats["brightness"] - baseline["brightness"]) / max(baseline["brightness"], 1)
        color_dev = self._color_deviation(stats, baseline)
        return bright_dev > self.protect_threshold or color_dev > self.protect_threshold

    def _update_ema(self, current_stats):
        alpha = self.ema_alpha
        for key in self.ema_stats:
            if key in current_stats:
                self.ema_stats[key] = (1 - alpha) * self.ema_stats[key] + alpha * current_stats[key]
        self.ema_stats["brightness"] = max(20, min(230, self.ema_stats["brightness"]))
        self.config["ema_baseline"] = self.ema_stats
        self.save_config_to_disk()

    def _color_deviation(self, stats, base):
        if base["avg_g"] > 0 and stats["avg_g"] > 0:
            dr = abs(stats["rg_ratio"] - base["rg_ratio"]) / max(base["rg_ratio"], 1e-5)
            db = abs(stats["bg_ratio"] - base["bg_ratio"]) / max(base["bg_ratio"], 1e-5)
            return max(dr, db)
        return 0.0

    def _frame_change_rate(self, current, last):
        if last is None or last["brightness"] == 0:
            return 0.0
        return abs(current["brightness"] - last["brightness"]) / last["brightness"]

    def compute_stats(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        b, g, r = cv2.split(img.astype(np.float32))
        avg_r = np.mean(r)
        avg_g = np.mean(g)
        avg_b = np.mean(b)
        return {
            "brightness": brightness,
            "avg_r": avg_r,
            "avg_g": avg_g,
            "avg_b": avg_b,
            "rg_ratio": avg_r / avg_g if avg_g > 0 else 1,
            "bg_ratio": avg_b / avg_g if avg_g > 0 else 1
        }

    def apply_correction(self, img, base_stats, current_stats):
        img_float = img.astype(np.float32)
        if current_stats["avg_g"] > 0 and base_stats["avg_g"] > 0:
            gain_r = (base_stats["avg_r"] / base_stats["avg_g"]) / (current_stats["avg_r"] / current_stats["avg_g"])
            gain_b = (base_stats["avg_b"] / base_stats["avg_g"]) / (current_stats["avg_b"] / current_stats["avg_g"])
        else:
            gain_r, gain_b = 1.0, 1.0
        gain_r = np.clip(gain_r, 0.7, 1.5)
        gain_b = np.clip(gain_b, 0.7, 1.5)
        b, g, r = cv2.split(img_float)
        r = r * gain_r
        b = b * gain_b
        img_float = cv2.merge([b, g, r])

        hsv = cv2.cvtColor(img_float.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        scale = base_stats["brightness"] / max(current_stats["brightness"], 1)
        scale = np.clip(scale, 0.3, 3.0)
        gamma = 1.0 / scale if scale != 0 else 1.0
        gamma = np.clip(gamma, 0.4, 2.5)
        v_channel = hsv[:, :, 2]
        v_normalized = v_channel / 255.0
        v_corrected = np.power(v_normalized, gamma) * 255.0
        hsv[:, :, 2] = np.clip(v_corrected, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    def save_config_to_disk(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置失败: {e}")

    def stop(self):
        self._running = False