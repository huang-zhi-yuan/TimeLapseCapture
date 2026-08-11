# settings_dialog.py
import os
from PyQt5.QtWidgets import (
    QDialog, QComboBox, QPushButton, QLineEdit,
    QFormLayout, QSpinBox, QCheckBox, QFileDialog,
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QDoubleSpinBox, QMessageBox
)
from camera_utils import list_cameras, open_camera_properties

class SettingsDialog(QDialog):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("延时摄影设置")
        self.setMinimumWidth(520)
        main_layout = QVBoxLayout()

        # ---- 基本设置 ----
        basic_group = QGroupBox("基本设置")
        basic_layout = QFormLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.setToolTip("选择要使用的摄像头")
        self.cameras = list_cameras()
        for idx, name in self.cameras:
            self.camera_combo.addItem(f"[{idx}] {name}", idx)
        basic_layout.addRow("摄像头:", self.camera_combo)
        btn_props = QPushButton("打开摄像头属性（手动固定参数）")
        btn_props.setToolTip("打开Windows摄像头驱动面板，可锁定白平衡、对焦等")
        btn_props.clicked.connect(self.open_props)
        basic_layout.addRow("", btn_props)

        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit()
        self.dir_edit.setReadOnly(True)
        self.dir_edit.setToolTip("照片存储根目录，按年/月/日自动创建子文件夹")
        btn_dir = QPushButton("选择...")
        btn_dir.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(btn_dir)
        basic_layout.addRow("存储根目录:", dir_layout)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 86400)
        self.interval_spin.setValue(3600)
        self.interval_spin.setSuffix(" 秒")
        self.interval_spin.setToolTip("两次拍摄间隔")
        basic_layout.addRow("拍摄间隔:", self.interval_spin)
        basic_group.setLayout(basic_layout)
        main_layout.addWidget(basic_group)

        # ---- 画质增强 ----
        quality_group = QGroupBox("画质增强")
        q_layout = QFormLayout()
        self.stack_check = QCheckBox("启用多帧堆栈降噪")
        self.stack_check.setToolTip("连续拍摄多帧取平均，降低随机噪声")
        self.stack_count = QSpinBox()
        self.stack_count.setRange(2, 10)
        self.stack_count.setValue(4)
        self.stack_count.setToolTip("堆栈帧数，越大降噪越好但耗时增加")
        q_layout.addRow(self.stack_check, self.stack_count)

        # 堆栈帧间间隔
        self.stack_interval_spin = QDoubleSpinBox()
        self.stack_interval_spin.setRange(0.0, 2.0)
        self.stack_interval_spin.setSingleStep(0.05)
        self.stack_interval_spin.setValue(0.1)
        self.stack_interval_spin.setToolTip("堆栈时帧与帧之间的等待时间（秒），值越小越不易产生重影")
        q_layout.addRow("堆栈帧间间隔:", self.stack_interval_spin)

        self.png_check = QCheckBox("输出无损PNG (已强制开启)")
        self.png_check.setChecked(True)
        self.png_check.setEnabled(False)
        q_layout.addRow(self.png_check)
        self.res_label = QLabel()
        q_layout.addRow("当前最佳分辨率:", self.res_label)
        quality_group.setLayout(q_layout)
        main_layout.addWidget(quality_group)

        # ---- 自动检测与修正 ----
        auto_group = QGroupBox("自动检测与修正")
        a_layout = QFormLayout()
        self.thresh_bright = QDoubleSpinBox()
        self.thresh_bright.setRange(0.01, 1.0)
        self.thresh_bright.setSingleStep(0.01)
        self.thresh_bright.setValue(0.08)
        a_layout.addRow("亮度偏差阈值:", self.thresh_bright)
        self.thresh_color = QDoubleSpinBox()
        self.thresh_color.setRange(0.01, 1.0)
        self.thresh_color.setSingleStep(0.01)
        self.thresh_color.setValue(0.10)
        a_layout.addRow("白平衡偏差阈值:", self.thresh_color)
        self.change_thresh = QDoubleSpinBox()
        self.change_thresh.setRange(0.01, 1.0)
        self.change_thresh.setSingleStep(0.01)
        self.change_thresh.setValue(0.15)
        a_layout.addRow("突变检测阈值:", self.change_thresh)
        self.ema_spin = QDoubleSpinBox()
        self.ema_spin.setRange(0.01, 1.0)
        self.ema_spin.setSingleStep(0.01)
        self.ema_spin.setValue(0.05)
        a_layout.addRow("基准适应速度:", self.ema_spin)
        self.protect_thresh = QDoubleSpinBox()
        self.protect_thresh.setRange(0.1, 0.8)
        self.protect_thresh.setSingleStep(0.05)
        self.protect_thresh.setValue(0.30)
        a_layout.addRow("EMA更新保护阈值:", self.protect_thresh)
        self.baseline_min = QSpinBox()
        self.baseline_min.setRange(10, 150)
        self.baseline_min.setValue(50)
        a_layout.addRow("基准亮度下限:", self.baseline_min)
        self.baseline_max = QSpinBox()
        self.baseline_max.setRange(100, 245)
        self.baseline_max.setValue(200)
        a_layout.addRow("基准亮度上限:", self.baseline_max)
        self.baseline_retry = QSpinBox()
        self.baseline_retry.setRange(1, 10)
        self.baseline_retry.setValue(3)
        a_layout.addRow("连续失败后启用默认基准:", self.baseline_retry)
        reset_btn = QPushButton("重置基准（下次拍摄建立新基准）")
        reset_btn.clicked.connect(self.reset_baseline)
        a_layout.addRow(reset_btn)
        self.severe_limit = QSpinBox()
        self.severe_limit.setRange(1, 20)
        self.severe_limit.setValue(3)
        a_layout.addRow("连续严重异常触发适应:", self.severe_limit)
        self.dyn_alpha = QDoubleSpinBox()
        self.dyn_alpha.setRange(0.05, 1.0)
        self.dyn_alpha.setSingleStep(0.05)
        self.dyn_alpha.setValue(0.3)
        a_layout.addRow("动态适应 Alpha:", self.dyn_alpha)
        self.dyn_protect = QDoubleSpinBox()
        self.dyn_protect.setRange(0.2, 0.9)
        self.dyn_protect.setSingleStep(0.05)
        self.dyn_protect.setValue(0.6)
        a_layout.addRow("动态保护阈值:", self.dyn_protect)
        auto_group.setLayout(a_layout)
        main_layout.addWidget(auto_group)

        # ---- 手动曝光控制 ----
        exp_group = QGroupBox("手动曝光控制")
        exp_layout = QFormLayout()
        self.exp_manual_check = QCheckBox("启用手动曝光")
        self.exp_manual_check.setToolTip("勾选后关闭自动曝光，使用固定值")
        self.exp_manual_check.toggled.connect(self.toggle_exposure_controls)
        exp_layout.addRow(self.exp_manual_check)
        self.exp_value_spin = QDoubleSpinBox()
        self.exp_value_spin.setToolTip("曝光值（-13最暗 ~ -1最亮）")
        self.exp_value_spin.setRange(-13.0, -1.0)
        self.exp_value_spin.setSingleStep(0.5)
        self.exp_value_spin.setValue(-6.0)
        self.exp_value_spin.setEnabled(False)
        exp_layout.addRow("曝光值:", self.exp_value_spin)
        self.test_exp_btn = QPushButton("测试曝光（拍摄一张）")
        self.test_exp_btn.clicked.connect(self.on_test_exposure)
        exp_layout.addRow(self.test_exp_btn)
        self.exp_status_label = QLabel("")
        exp_layout.addRow("结果:", self.exp_status_label)
        exp_group.setLayout(exp_layout)
        main_layout.addWidget(exp_group)

        # ---- 摄像头占用重试 ----
        retry_group = QGroupBox("摄像头占用自动重试")
        r_layout = QFormLayout()
        self.retry_count = QSpinBox()
        self.retry_count.setRange(1, 20)
        self.retry_count.setValue(5)
        r_layout.addRow("最大重试次数:", self.retry_count)
        self.retry_delay = QSpinBox()
        self.retry_delay.setRange(5, 120)
        self.retry_delay.setValue(10)
        self.retry_delay.setSuffix(" 秒")
        r_layout.addRow("重试间隔:", self.retry_delay)
        retry_group.setLayout(r_layout)
        main_layout.addWidget(retry_group)

        # ---- 异常暗帧保护 ----
        abnormal_group = QGroupBox("异常暗帧保护")
        a_layout2 = QFormLayout()
        self.frame_retry_spin = QSpinBox()
        self.frame_retry_spin.setRange(1, 10)
        self.frame_retry_spin.setValue(3)
        self.frame_retry_spin.setToolTip("检测到全黑/极暗帧时的重新获取次数")
        a_layout2.addRow("异常暗帧重试次数:", self.frame_retry_spin)
        abnormal_group.setLayout(a_layout2)
        main_layout.addWidget(abnormal_group)

        # ---- 启动行为 ----
        start_group = QGroupBox("启动行为")
        start_layout = QVBoxLayout()
        self.autostart_check = QCheckBox("开机自动启动程序")
        start_layout.addWidget(self.autostart_check)
        self.auto_capture_check = QCheckBox("程序启动时自动开始拍摄")
        start_layout.addWidget(self.auto_capture_check)
        start_group.setLayout(start_layout)
        main_layout.addWidget(start_group)

        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存并应用")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.load_current_config()

    def load_current_config(self):
        cfg = self.engine.config
        idx = self.camera_combo.findData(cfg.get("camera_index", 0))
        if idx >= 0:
            self.camera_combo.setCurrentIndex(idx)
        self.dir_edit.setText(cfg.get("root_directory", ""))
        self.interval_spin.setValue(cfg.get("interval_seconds", 3600))
        self.stack_check.setChecked(cfg.get("stack_enabled", True))
        self.stack_count.setValue(cfg.get("stack_count", 4))
        self.stack_interval_spin.setValue(cfg.get("stack_frame_interval", 0.1))
        self.res_label.setText(f"{cfg.get('best_width',0)} x {cfg.get('best_height',0)}")
        self.thresh_bright.setValue(cfg.get("threshold_brightness", 0.08))
        self.thresh_color.setValue(cfg.get("threshold_color", 0.10))
        self.change_thresh.setValue(cfg.get("threshold_change_rate", 0.15))
        self.ema_spin.setValue(cfg.get("ema_alpha", 0.05))
        self.protect_thresh.setValue(cfg.get("ema_protect_threshold", 0.30))
        self.baseline_min.setValue(cfg.get("baseline_min_brightness", 50))
        self.baseline_max.setValue(cfg.get("baseline_max_brightness", 200))
        self.baseline_retry.setValue(cfg.get("baseline_retry_limit", 3))
        self.severe_limit.setValue(cfg.get("consecutive_severe_limit", 3))
        self.dyn_alpha.setValue(cfg.get("dynamic_alpha_high", 0.3))
        self.dyn_protect.setValue(cfg.get("dynamic_protect_high", 0.6))
        self.retry_count.setValue(cfg.get("capture_retry_count", 5))
        self.retry_delay.setValue(cfg.get("capture_retry_delay", 10))
        self.autostart_check.setChecked(cfg.get("autostart", False))
        self.auto_capture_check.setChecked(cfg.get("auto_start_capture", False))
        self.exp_manual_check.setChecked(cfg.get("exposure_manual", False))
        self.exp_value_spin.setValue(cfg.get("exposure_value", -6.0))
        self.frame_retry_spin.setValue(cfg.get("frame_retry_count", 3))
        self.toggle_exposure_controls(self.exp_manual_check.isChecked())

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择存储根目录")
        if dir_path:
            self.dir_edit.setText(dir_path)

    def open_props(self):
        idx = self.camera_combo.currentData()
        if idx is not None:
            open_camera_properties(idx)
        else:
            QMessageBox.warning(self, "错误", "请先选择摄像头")

    def reset_baseline(self):
        self.engine.config["ema_baseline"] = None
        QMessageBox.information(self, "已重置", "下次拍摄时将建立新的动态基准。")

    def toggle_exposure_controls(self, checked):
        self.exp_value_spin.setEnabled(checked)

    def apply_ui_to_config(self):
        self.engine.config["exposure_manual"] = self.exp_manual_check.isChecked()
        self.engine.config["exposure_value"] = self.exp_value_spin.value()

    def on_test_exposure(self):
        self.apply_ui_to_config()
        success, msg = self.engine.test_exposure()
        if success:
            self.exp_status_label.setText(msg)
            QMessageBox.information(self, "测试结果", msg)
        else:
            self.exp_status_label.setText("测试失败：" + msg)
            QMessageBox.warning(self, "测试失败", msg)

    def save_settings(self):
        new_cfg = {
            "camera_index": self.camera_combo.currentData(),
            "root_directory": self.dir_edit.text(),
            "interval_seconds": self.interval_spin.value(),
            "stack_enabled": self.stack_check.isChecked(),
            "stack_count": self.stack_count.value(),
            "stack_frame_interval": self.stack_interval_spin.value(),
            "threshold_brightness": self.thresh_bright.value(),
            "threshold_color": self.thresh_color.value(),
            "threshold_change_rate": self.change_thresh.value(),
            "ema_alpha": self.ema_spin.value(),
            "ema_protect_threshold": self.protect_thresh.value(),
            "baseline_min_brightness": self.baseline_min.value(),
            "baseline_max_brightness": self.baseline_max.value(),
            "baseline_retry_limit": self.baseline_retry.value(),
            "consecutive_severe_limit": self.severe_limit.value(),
            "dynamic_alpha_high": self.dyn_alpha.value(),
            "dynamic_protect_high": self.dyn_protect.value(),
            "capture_retry_count": self.retry_count.value(),
            "capture_retry_delay": self.retry_delay.value(),
            "autostart": self.autostart_check.isChecked(),
            "auto_start_capture": self.auto_capture_check.isChecked(),
            "exposure_manual": self.exp_manual_check.isChecked(),
            "exposure_value": self.exp_value_spin.value(),
            "frame_retry_count": self.frame_retry_spin.value()
        }
        self.engine.update_config(new_cfg)
        self.accept()