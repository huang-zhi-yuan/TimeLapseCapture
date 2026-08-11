@echo off
chcp 65001 >nul
title TimeLapse 自启动安装程序

set "TASK_NAME=TimeLapseAutoStart"
set "CUR_DIR=%~dp0"

:: 1. 检查主程序是否存在
if not exist "%CUR_DIR%TimeLapseCapture.exe" (
    echo [错误] 当前文件夹找不到 TimeLapseCapture.exe！
    echo 请将此脚本放在与程序相同的目录下。
    pause
    exit /b
)

:: 2. 自动生成启动器（利用 %~dp0 实现路径自适应）
echo [1/3] 正在生成自适应启动器...
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo start /b "" "TimeLapseCapture.exe"
) > "%CUR_DIR%TimeLapse_Launcher.bat"

:: 3. 删除旧任务（如有）
echo [2/3] 正在清理旧任务...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: 4. 创建计划任务（使用当前文件夹的绝对路径，由脚本自动获取）
echo [3/3] 正在安装系统自启动任务...
schtasks /create /tn "%TASK_NAME%" /tr "%CUR_DIR%TimeLapse_Launcher.bat" /sc onstart /ru SYSTEM /rl HIGHEST /delay 0000:30 /f

:: 5. 判断结果
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  ✅ 安装成功！
    echo  任务名称：%TASK_NAME%
    echo  程序位置：%CUR_DIR%
    echo  启动时机：系统开机后 30 秒（延迟启动）
    echo  运行权限：系统最高权限（后台静默）
    echo ========================================
    echo.
    echo 提示：如需卸载，请以管理员身份运行：
    echo schtasks /delete /tn "%TASK_NAME%" /f
) else (
    echo.
    echo  ❌ 安装失败！请确保已右键选择“以管理员身份运行”。
)

pause