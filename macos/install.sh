#!/bin/bash
# Camera Blocker - Установка для MacOS

set -e

echo "========================================"
echo " Camera Blocker - Установка (macOS)"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: Требуются права root."
    echo "Запустите: sudo ./install.sh"
    exit 1
fi

echo "Права root подтверждены."
echo ""

if [ -f /var/tmp/camera_blocker.disabled ]; then
    echo "Обнаружен маркер предыдущего удаления."
    echo ""
    read -p "Продолжить установку? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Установка отменена."
        exit 0
    fi
    rm -f /var/tmp/camera_blocker.disabled
    echo "Маркер удален, продолжаем установку."
    echo ""
fi

echo "Создание директорий..."
mkdir -p /usr/local/bin/camera-blocker
mkdir -p /var/log/camera-blocker
mkdir -p /Library/LaunchDaemons

echo "Копирование файлов..."
cp camera_blocker.py /usr/local/bin/camera-blocker/
chmod +x /usr/local/bin/camera-blocker/camera_blocker.py

echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: Python3 не найден."
    echo "Установите Python3 (например, через brew install python3) и запустите установку снова."
    exit 1
fi

echo "Создание Launch Daemon..."
cat > /Library/LaunchDaemons/com.camerablocker.daemon.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.camerablocker.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/usr/local/bin/camera-blocker/camera_blocker.py</string>
        <string>--start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/camera-blocker/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/camera-blocker/stderr.log</string>
</dict>
</plist>
EOF

chmod 644 /Library/LaunchDaemons/com.camerablocker.daemon.plist
chown root:wheel /Library/LaunchDaemons/com.camerablocker.daemon.plist

echo "Создание команд управления..."
cat > /usr/local/bin/camera-blocker-start << 'EOF'
#!/bin/bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --start
EOF

cat > /usr/local/bin/camera-blocker-stop << 'EOF'
#!/bin/bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop
EOF

cat > /usr/local/bin/camera-blocker-status << 'EOF'
#!/bin/bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --status
EOF

chmod +x /usr/local/bin/camera-blocker-*

echo "Блокировка камеры..."
python3 /usr/local/bin/camera-blocker/camera_blocker.py --block

echo "Загрузка Launch Daemon..."
launchctl load /Library/LaunchDaemons/com.camerablocker.daemon.plist 2>/dev/null || true

echo ""
echo "========================================"
echo " УСТАНОВКА ЗАВЕРШЕНА"
echo "========================================"
echo ""
echo "- Камера заблокирована."
echo "- Автозапуск настроен."
echo ""
echo "Используйте команды: camera-blocker-start, camera-blocker-stop, camera-blocker-status."
echo ""
echo "Берегите свою приватность!"
echo ""

