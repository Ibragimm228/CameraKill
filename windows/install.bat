@echo off
chcp 65001 >nul
echo ========================================
echo  Camera Blocker - Установка (Windows)
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Ошибка: Требуются права администратора.
    echo Запустите этот файл от имени администратора.
    pause
    exit /b 1
)

echo Права администратора подтверждены.
echo.

powershell -Command "dir '%~dp0' -Recurse | Unblock-File" 2>nul

if exist "C:\ProgramData\CameraBlocker.disabled" (
    echo Обнаружен маркер предыдущего удаления.
    echo.
    choice /C YN /M "Camera Blocker был ранее удален. Продолжить установку?"
    if errorlevel 2 (
        echo.
        echo Установка отменена.
        pause
        exit /b 0
    )
    del /F /Q "C:\ProgramData\CameraBlocker.disabled" 2>nul
    echo Маркер удален, продолжаем установку.
    echo.
)

echo Создание директорий...
if not exist "C:\ProgramData\CameraBlocker" mkdir "C:\ProgramData\CameraBlocker"
if not exist "C:\ProgramData\CameraBlocker\logs" mkdir "C:\ProgramData\CameraBlocker\logs"

echo Копирование файлов...
copy /Y "camera_blocker.py" "C:\ProgramData\CameraBlocker\camera_blocker.py" >nul

echo Проверка Python...
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    set PYTHON_CMD=py
    py --version >nul 2>&1
    if %errorLevel% neq 0 (
        echo Ошибка: Python не найден.
        pause
        exit /b 1
    )
)

echo Создание задачи автозапуска...
schtasks /create /tn "CameraBlocker" /tr "%PYTHON_CMD% C:\ProgramData\CameraBlocker\camera_blocker.py --start" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1

echo Создание ярлыков...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Camera Blocker - Запустить.lnk'); $Shortcut.TargetPath = '%PYTHON_CMD%'; $Shortcut.Arguments = 'C:\ProgramData\CameraBlocker\camera_blocker.py --start'; $Shortcut.WorkingDirectory = 'C:\ProgramData\CameraBlocker'; $Shortcut.IconLocation = 'shell32.dll,48'; $Shortcut.Save()"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Camera Blocker - Остановить.lnk'); $Shortcut.TargetPath = '%PYTHON_CMD%'; $Shortcut.Arguments = 'C:\ProgramData\CameraBlocker\camera_blocker.py --stop'; $Shortcut.WorkingDirectory = 'C:\ProgramData\CameraBlocker'; $Shortcut.IconLocation = 'shell32.dll,47'; $Shortcut.Save()"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Camera Blocker - Статус.lnk'); $Shortcut.TargetPath = '%PYTHON_CMD%'; $Shortcut.Arguments = 'C:\ProgramData\CameraBlocker\camera_blocker.py --status'; $Shortcut.WorkingDirectory = 'C:\ProgramData\CameraBlocker'; $Shortcut.IconLocation = 'shell32.dll,24'; $Shortcut.Save()"

echo Блокировка камер...
%PYTHON_CMD% "C:\ProgramData\CameraBlocker\camera_blocker.py" --block
echo.

echo ========================================
echo  УСТАНОВКА ЗАВЕРШЕНА
echo ========================================
echo.
echo - Камеры заблокированы.
echo - Ярлыки созданы на рабочем столе.
echo - Автозапуск настроен.
echo.
echo Берегите свою приватность!
echo.
pause

