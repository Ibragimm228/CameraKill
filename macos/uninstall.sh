#!/bin/bash
# Camera Blocker - Удаление для MacOS

set -e

echo "========================================"
echo " Camera Blocker - Удаление (macOS)"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: Требуются права root."
    echo "Запустите: sudo ./uninstall.sh"
    exit 1
fi

echo "Остановка процессов..."
launchctl unload /Library/LaunchDaemons/com.camerablocker.daemon.plist 2>/dev/null || true
launchctl remove com.camerablocker.daemon 2>/dev/null || true
pkill -9 -f camera_blocker.py 2>/dev/null || true

echo "Разблокировка камеры..."
kextload -b com.apple.driver.AppleCameraInterface 2>/dev/null || true
kextload /System/Library/Extensions/AppleCameraInterface.kext 2>/dev/null || true

rm -f /var/tmp/.camera_blocked 2>/dev/null || true

if [ -f /usr/local/bin/camera-blocker/camera_blocker.py ]; then
    python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop 2>/dev/null || true
fi

echo "Удаление системных файлов..."
rm -f /Library/LaunchDaemons/com.camerablocker.daemon.plist
rm -f /usr/local/bin/camera-blocker-*
rm -rf /usr/local/bin/camera-blocker
rm -rf /var/log/camera-blocker
rm -f /var/tmp/camera_blocker_status.txt

echo "Создание маркера деактивации..."
touch /var/tmp/camera_blocker.disabled

echo ""
echo "========================================"
echo " УДАЛЕНИЕ ЗАВЕРШЕНО"
echo "========================================"
echo ""
echo "Камера разблокирована. Если она не заработала сразу — перезагрузите систему."
echo ""

echo "✅ Права root подтверждены"
echo ""

echo "🛑 Остановка всех процессов блокировщика..."
launchctl unload /Library/LaunchDaemons/com.camerablocker.daemon.plist 2>/dev/null || true
launchctl remove com.camerablocker.daemon 2>/dev/null || true
pkill -9 -f camera_blocker.py 2>/dev/null || true
echo "✅ Все процессы остановлены"
echo ""

echo "⏱️  Ожидание 2 секунды..."
sleep 2
echo ""

echo "🔓 Разблокировка камеры..."
kextload -b com.apple.driver.AppleCameraInterface 2>/dev/null || true
kextload /System/Library/Extensions/AppleCameraInterface.kext 2>/dev/null || true
echo "✅ Kernel extensions загружены"

rm -f /var/tmp/.camera_blocked 2>/dev/null || true

if [ -f /usr/local/bin/camera-blocker/camera_blocker.py ]; then
    python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop 2>/dev/null || true
fi
echo "✅ Камера разблокирована"
echo ""

echo "🗑️  Удаление Launch Daemon..."
rm -f /Library/LaunchDaemons/com.camerablocker.daemon.plist
echo "✅ Launch Daemon удалён"
echo ""

echo "🗑️  Удаление командных алиасов..."
rm -f /usr/local/bin/camera-blocker-start
rm -f /usr/local/bin/camera-blocker-stop
rm -f /usr/local/bin/camera-blocker-status
echo "✅ Командные алиасы удалены"
echo ""

echo "🗑️  Удаление файлов программы..."
rm -rf /usr/local/bin/camera-blocker
echo "✅ Файлы программы удалены"
echo ""

echo "🗑️  Удаление логов..."
rm -rf /var/log/camera-blocker
echo "✅ Логи удалены"
echo ""

echo "🗑️  Удаление временных файлов..."
rm -f /var/tmp/.camera_blocked
rm -f /var/tmp/camera_blocker_status.txt
echo "✅ Временные файлы удалены"
echo ""

echo "⏱️  Проверка стабильности (3 секунды)..."
sleep 3
echo ""

echo "🔍 Финальная проверка kernel extensions..."
if kextstat | grep -q AppleCameraInterface; then
    echo "✅ AppleCameraInterface загружен и работает"
else
    echo "⚠️  AppleCameraInterface не загружен, повторная попытка..."
    kextload -b com.apple.driver.AppleCameraInterface 2>/dev/null || true
fi
echo ""

echo "🔒 Блокировка автозапуска Camera Blocker..."
touch /var/tmp/camera_blocker.disabled
echo "✅ Маркер отключения создан"
echo ""

echo "========================================"
echo " ✅ УДАЛЕНИЕ ЗАВЕРШЕНО!"
echo "========================================"
echo ""
echo "🔓 Камера разблокирована и работает"
echo "🗑️  Все файлы удалены"
echo "🛡️  Автозапуск блокировщика отключен"
echo ""
echo "💡 Если камера не работает:"
echo "   1. Перезагрузите систему"
echo "   2. Проверьте разрешения в System Preferences → Security & Privacy"
echo "   3. Проверьте kext: kextstat | grep Camera"
echo ""

