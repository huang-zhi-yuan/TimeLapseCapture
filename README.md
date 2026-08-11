
<body>

<h1>TimeLapseCapture v2.0.1</h1>
<p><strong>High-Quality Adaptive Timelapse Tool for Windows</strong><br>
<em>高画质自适应延时摄影工具</em></p>

<div class="badges">
    <img src="https://img.shields.io/badge/platform-Windows-blue" alt="platform">
    <img src="https://img.shields.io/badge/python-3.8%2B-brightgreen" alt="python">
    <img src="https://img.shields.io/badge/license-Proprietary-red" alt="license">
</div>

<!-- ==================== 英文部分 ==================== -->
<div class="en-section">
<h2>English</h2>

<h3>✨ Key Features</h3>
<ul>
    <li>
        <strong>Multi-frame Stacking &amp; Denoising</strong><br>
        The camera remains open and continuously captures 2–10 frames for averaging, effectively suppressing random noise. The inter‑frame interval is adjustable (0–2s) to reduce motion blur.
    </li>
    <li>
        <strong>Intelligent Dynamic Baseline &amp; Auto-Correction</strong><br>
        Automatically establishes a brightness/white-balance baseline (EMA) and monitors deviations in real time. Brightness is compensated using <strong>gamma correction</strong>, preserving highlight and shadow details.<br>
        Abnormal frames are skipped during baseline updates; a fast‑adaptation mode activates after consecutive severe anomalies.
    </li>
    <li>
        <strong>Manual Exposure Lock</strong><br>
        Disable the camera’s auto-exposure and lock a fixed exposure value (-13 to -1), eliminating flicker. A one‑click test exposure function is included for immediate feedback.
    </li>
    <li>
        <strong>Fully Automatic Startup with Windows</strong><br>
        Uses the Windows Registry Run key (HKCU) — no administrator privileges required. A 30‑second delay after login ensures smooth system initialization.
    </li>
    <li>
        <strong>Abnormal Dark Frame Protection</strong><br>
        Detects completely black or extremely dark frames and automatically retries capturing, preventing bad frames from polluting your dataset.
    </li>
    <li>
        <strong>System Tray Resident</strong><br>
        Runs minimized in the system tray. Right‑click the tray icon to open settings, take a manual shot, or exit. A fallback icon ensures the tray icon is always visible.
    </li>
    <li>
        <strong>Highly Customizable</strong><br>
        All parameters (interval, stacking count, thresholds, adaptation speed, etc.) can be adjusted through the graphical interface and are saved persistently.
    </li>
</ul>

<h3>🆕 What’s New in v2.0.1</h3>
<ul>
    <li><strong>Manual Exposure Control</strong> – Lock exposure with hardware-level support.</li>
    <li><strong>GUI‑Configurable Stack Frame Interval</strong> – Balance noise reduction and motion blur.</li>
    <li><strong>Gamma‑Based Brightness Correction</strong> – More natural highlight protection.</li>
    <li><strong>Abnormal Dark Frame Retry</strong> – Automatically discards extremely dark frames.</li>
    <li><strong>Registry Startup</strong> – More reliable, no admin rights required.</li>
    <li><strong>Performance</strong> – Camera stays open during stacking for faster capture and stable exposure.</li>
    <li><strong>Bug Fixes</strong> – Tray icon visibility, missing imports, project structure improvements.</li>
</ul>

<h3>📥 Installation &amp; Usage</h3>
<h4>Run from source</h4>
<pre><code>pip install opencv-python numpy PyQt5
python main.py</code></pre>
<p>(Windows, Python 3.8+)</p>

<h4>Build standalone EXE</h4>
<pre><code>pyinstaller --onefile --noconsole --icon=camera_icon.ico --add-data "camera_icon.ico;." --name="TimeLapseCapture" main.py</code></pre>
<p>The generated <code>dist/TimeLapseCapture.exe</code> can be run directly.</p>

<h3>⚙️ Key Configuration Options</h3>
<table>
    <tr>
        <th>Category</th>
        <th>Parameter</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>Image Quality</td>
        <td>Stack frames / Interval</td>
        <td>Balance between noise reduction and motion blur</td>
    </tr>
    <tr>
        <td>Auto Detection &amp; Correction</td>
        <td>Brightness/Color thresholds, EMA speed</td>
        <td>Adjust correction sensitivity and baseline stability</td>
    </tr>
    <tr>
        <td>Manual Exposure Control</td>
        <td>Exposure value</td>
        <td>Lock camera exposure to avoid automatic brightness changes</td>
    </tr>
    <tr>
        <td>Anomaly Protection</td>
        <td>Dark frame retry count</td>
        <td>Number of re‑capture attempts when a near‑black frame is detected</td>
    </tr>
</table>
</div>

<hr>

<!-- ==================== 中文部分 ==================== -->
<div class="zh-section">
<h2>中文</h2>

<h3>✨ 核心功能</h3>
<ul>
    <li>
        <strong>多帧堆栈降噪</strong><br>
        摄像头保持常开，连续拍摄 2–10 帧取平均，有效抑制随机噪点。帧间间隔可调（0–2秒），减少运动重影。
    </li>
    <li>
        <strong>智能动态基准与自动校正</strong><br>
        自动建立亮度/白平衡基准（EMA），实时检测偏差，并通过<strong>伽马校正</strong>补偿亮度，保护高光与暗部细节。<br>
        异常帧自动跳过更新，防止基准污染；连续严重异常后自动切换至快速适应模式。
    </li>
    <li>
        <strong>手动曝光锁定</strong><br>
        可关闭摄像头自动曝光，锁定固定曝光值（-13~-1），消除画面闪烁。内置一键测试曝光功能，即时反馈效果。
    </li>
    <li>
        <strong>开机自动启动</strong><br>
        使用 Windows 注册表 Run 键（HKCU），无需管理员权限。登录后延迟 30 秒启动，确保系统初始化完成。
    </li>
    <li>
        <strong>异常暗帧保护</strong><br>
        自动检测全黑或极暗帧并重新获取，避免废片污染数据集。
    </li>
    <li>
        <strong>系统托盘驻留</strong><br>
        最小化至系统托盘运行，右键菜单可打开设置、手动拍摄或退出。带图标回退机制，确保托盘图标始终可见。
    </li>
    <li>
        <strong>高度可定制</strong><br>
        所有参数（间隔、堆栈帧数、阈值、适应速度等）均可在图形界面中调整，并持久化保存。
    </li>
</ul>

<h3>🆕 v2.0.1 更新内容</h3>
<ul>
    <li><strong>手动曝光控制</strong> – 新增曝光锁定开关与曝光值调节，硬件级关闭自动曝光。</li>
    <li><strong>堆栈帧间隔 GUI 配置</strong> – 可在设置界面直接调整帧间等待时间，平衡降噪与运动模糊。</li>
    <li><strong>伽马亮度校正</strong> – 用伽马校正替代线性缩放，更自然地保护高光细节。</li>
    <li><strong>异常暗帧重试</strong> – 检测到极暗帧自动丢弃并重新拍摄。</li>
    <li><strong>注册表开机自启</strong> – 改用 <code>HKCU\Run</code> 注册表项，更可靠且无需管理员权限。</li>
    <li><strong>性能优化</strong> – 堆栈拍摄时摄像头常开，大幅缩短拍摄时间并消除曝光波动。</li>
    <li><strong>问题修复</strong> – 修复托盘图标不显示、缺少导入等错误，并优化项目结构。</li>
</ul>

<h3>📥 安装与使用</h3>
<h4>从源码运行</h4>
<pre><code>pip install opencv-python numpy PyQt5
python main.py</code></pre>
<p>（推荐 Windows 环境，Python 3.8+）</p>

<h4>打包为独立 EXE</h4>
<pre><code>pyinstaller --onefile --noconsole --icon=camera_icon.ico --add-data "camera_icon.ico;." --name="TimeLapseCapture" main.py</code></pre>
<p>生成的 <code>dist/TimeLapseCapture.exe</code> 可直接运行。</p>

<h4>下载链接</h4>
<pre><code>https://release-assets.githubusercontent.com/github-production-release-asset/1330579873/6a87012a-ddb1-4bc2-a3c0-b54108b60b6e?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-08-11T08%3A26%3A42Z&rscd=attachment%3B+filename%3DTimeLapseCapture.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-08-11T07%3A26%3A27Z&ske=2026-08-11T08%3A26%3A42Z&sks=b&skv=2018-11-09&sig=%2BEr1kon0m5Axz%2FsLo%2FYdkjKKx8HGRppVyFpLASmogTg%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc4NjQzNzc0OCwibmJmIjoxNzg2NDM0MTQ4LCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.fFpWQiaoi56XJAOS_iI8LbQRNidowoS7unTIQ7upMvI&response-content-disposition=attachment%3B%20filename%3DTimeLapseCapture.exe&response-content-type=application%2Foctet-stream</code></pre>
<pre><code>https://github.com/huang-zhi-yuan/TimeLapseCapture/releases/tag/2.0.1</code></pre>
<p> 可直接运行。</p>

<h3>⚙️ 主要可配置项</h3>
<table>
    <tr>
        <th>类别</th>
        <th>参数</th>
        <th>说明</th>
    </tr>
    <tr>
        <td>画质增强</td>
        <td>堆栈帧数 / 帧间间隔</td>
        <td>平衡降噪强度与运动模糊</td>
    </tr>
    <tr>
        <td>自动检测与校正</td>
        <td>亮度/色彩阈值、EMA 速度</td>
        <td>调节校正灵敏度与基准稳定性</td>
    </tr>
    <tr>
        <td>手动曝光控制</td>
        <td>曝光值</td>
        <td>锁定摄像头曝光，避免自动亮度变化</td>
    </tr>
    <tr>
        <td>异常保护</td>
        <td>暗帧重试次数</td>
        <td>检测到近全黑帧时的重新获取次数</td>
    </tr>
</table>
</div>

<hr>

<h2>📄 License / 许可证</h2>
<p>© 智慧猿（黄智源huangzhiyuan). All rights reserved.<br>
© 智慧猿（黄智源huangzhiyuan)。保留所有权利。</p>

<p><strong>Enjoy rock-solid timelapses! 🌄<br>
享受稳如磐石的延时摄影体验！ 🌄</strong></p>

</body>
</html>
