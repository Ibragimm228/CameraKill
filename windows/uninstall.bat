@echo off
chcp 65001 >nul
echo ========================================
echo  Camera Blocker - Удаление (Windows)
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Ошибка: Требуются права администратора.
    echo Запустите этот файл от имени администратора.
    pause
    exit /b 1
)

echo Остановка процессов...
schtasks /end /tn "CameraBlocker" >nul 2>&1
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*camera_blocker*' } | Stop-Process -Force" 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *camera_blocker*" >nul 2>&1

echo Разблокировка камер...
python "C:\ProgramData\CameraBlocker\camera_blocker.py" --stop 2>nul
if %errorLevel% neq 0 (
    powershell -Command "Get-PnpDevice | Where-Object { ($_.Class -eq 'Camera' -or $_.Class -eq 'Image' -or $_.FriendlyName -like '*camera*' -or $_.FriendlyName -like '*webcam*') -and $_.Status -eq 'Error' } | ForEach-Object { Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false }"
)

echo Удаление задачи автозапуска...
schtasks /delete /tn "CameraBlocker" /f >nul 2>&1

echo Удаление ярлыков...
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Запустить.lnk" 2>nul
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Остановить.lnk" 2>nul
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Статус.lnk" 2>nul

echo Удаление файлов...
if exist "C:\ProgramData\CameraBlocker" rmdir /S /Q "C:\ProgramData\CameraBlocker"

echo Создание маркера деактивации...
if not exist "C:\ProgramData" mkdir "C:\ProgramData"
echo CAMERA_BLOCKER_DISABLED > "C:\ProgramData\CameraBlocker.disabled"

echo.
echo ========================================
echo  УДАЛЕНИЕ ЗАВЕРШЕНО
echo ========================================
echo.
echo Камеры должны быть доступны. Если нет — проверьте Диспетчер устройств.
echo.
pause

