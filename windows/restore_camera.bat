@echo off
chcp 65001 >nul
echo ========================================
echo  🔧 ВОССТАНОВЛЕНИЕ КАМЕРЫ
echo ========================================
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Ошибка: Требуются права администратора.
    pause
    exit /b 1
)

echo Остановка процессов...
schtasks /end /tn "CameraBlocker" >nul 2>&1
schtasks /delete /tn "CameraBlocker" /f >nul 2>&1
powershell -Command "Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*camera_blocker*' } | Stop-Process -Force"
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *camera_blocker*" >nul 2>&1

echo Включение камер...
powershell -Command "Get-PnpDevice | Where-Object { ($_.Class -eq 'Camera' -or $_.Class -eq 'Image' -or $_.FriendlyName -like '*camera*' -or $_.FriendlyName -like '*webcam*') -and $_.Status -eq 'Error' } | ForEach-Object { Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false }"

echo Удаление остатков программы...
if exist "C:\ProgramData\CameraBlocker" rmdir /S /Q "C:\ProgramData\CameraBlocker"
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Запустить.lnk" 2>nul
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Остановить.lnk" 2>nul
del /F /Q "%USERPROFILE%\Desktop\Camera Blocker - Статус.lnk" 2>nul

echo Создание маркера деактивации...
if not exist "C:\ProgramData" mkdir "C:\ProgramData"
echo CAMERA_BLOCKER_DISABLED > "C:\ProgramData\CameraBlocker.disabled"

echo.
echo ========================================
echo  ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО
echo ========================================
echo.
echo Камеры должны быть доступны. Если нет — перезагрузите компьютер или проверьте Диспетчер устройств.
echo.
pause

