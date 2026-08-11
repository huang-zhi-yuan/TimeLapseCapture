# TimeLapseCapture – High‑Quality Adaptive Time‑Lapse Photography（中文见后面）

A Windows time‑lapse capture tool built with Python, OpenCV, and PyQt5. Designed for long‑term fixed‑camera shooting, it combines **multi‑frame stacking noise reduction**, **manual exposure lock**, **intelligent white balance / brightness correction**, and **gamma optimization** to deliver stable, clean sequences – free from flicker and color drift.

---

## ✨ Features

- 📷 **Multi‑frame stacking** – Captures multiple consecutive frames and averages them to suppress random noise. Number of frames and inter‑frame interval are adjustable.
- 🔒 **Manual exposure lock** – Directly controls the camera's exposure value, eliminating brightness fluctuations caused by automatic exposure.
- 🎨 **Auto white balance & brightness correction** – Continuously detects and corrects color/brightness deviations based on an exponential moving average (EMA) baseline.
- 📈 **Gamma correction** – Replaces linear scaling with gamma adjustment; brightens shadows while preserving highlights for a more natural look.
- 🛡️ **Anomaly protection** – Automatically discards near‑black frames and retries; anomalous frames do not contaminate the baseline. Dynamic adaptation handles gradual lighting changes.
- 🖥️ **System tray operation** – Runs silently in the background. A right‑click menu provides quick access to settings and manual capture.
- 🚀 **Auto‑start with Windows** – Uses the registry to launch the program on logon, with a configurable delayed start to keep the system responsive.
- ⚙️ **Full GUI configuration** – All parameters can be adjusted via a graphical settings dialog. Changes take effect immediately and are saved persistently.




# TimeLapse Capture – 高画质自适应延时摄影

基于 Python + OpenCV + PyQt5 的 Windows 延时摄影工具，专为长时间固定机位拍摄设计。  
通过**多帧堆栈降噪**、**手动曝光锁定**、**智能白平衡/亮度校正**与**伽马优化**，确保视频序列稳定、纯净，告别闪烁与色彩漂移。

## ✨ 核心功能

- 📷 **多帧堆栈降噪** – 连续拍摄多帧取平均，有效抑制随机噪声，可调节帧数与帧间隔
- 🔒 **手动曝光锁定** – 直接控制摄像头曝光值，彻底杜绝自动曝光导致的明暗跳动
- 🎨 **自动白平衡 & 亮度校正** – 基于 EMA 动态基准，实时检测并修正色彩/亮度偏差
- 📈 **伽马校正** – 替代线性缩放，提亮暗部同时保护高光，画面更自然
- 🛡️ **异常保护机制** – 全黑帧自动丢弃重试，异常帧不污染基准，动态适应环境光变化
- 🖥️ **系统托盘运行** – 后台静默工作，右键菜单快速设置、手动拍摄
- 🚀 **开机自启** – 通过注册表实现登录后自动运行，延迟启动保证系统流畅
- ⚙️ **全 GUI 配置** – 所有参数可视化调整，实时生效，支持保存/加载

