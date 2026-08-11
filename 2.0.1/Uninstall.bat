@echo off
chcp 65001 >nul
title TimeLapse 自启动卸载程序

:: 检查是否以管理员身份运行
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 请右键选择“以管理员身份运行”此脚本！
    pause
    exit /b
)

set "TASK_NAME=TimeLapseAutoStart"
set "CUR_DIR=%~dp0"

echo ========================================
echo    TimeLapse 自启动卸载程序
echo ========================================
echo.

:: 1. 删除系统计划任务
echo [1/2] 正在删除系统自启动任务...
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

if %errorlevel% equ 0 (
    echo        ✅ 任务 "%TASK_NAME%" 已成功删除。
) else (
    echo        ⚠️ 未找到任务 "%TASK_NAME%"（可能已被手动删除）。
)

:: 2. 删除安装时自动生成的启动器文件
echo [2/2] 正在清理生成的启动器文件...
if exist "%CUR_DIR%TimeLapse_Launcher.bat" (
    del /f /q "%CUR_DIR%TimeLapse_Launcher.bat"
    echo        ✅ 启动器文件 TimeLapse_Launcher.bat 已删除。
) else (
    echo        ⚠️ 启动器文件不存在，无需清理。
)

echo.
echo ========================================
echo   ✅ 卸载完成！
echo    主程序 TimeLapseCapture.exe 未被删除，保留在当前文件夹。
echo    如需彻底移除程序，请手动删除该 EXE 文件。
echo ========================================
pause