#!/bin/bash
set -e
if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: Требуются права root."
    exit 1
fi
launchctl unload /Library/LaunchDaemons/com.camerablocker.daemon.plist 2>/dev/null || true
launchctl remove com.camerablocker.daemon 2>/dev/null || true
pkill -9 -f camera_blocker.py 2>/dev/null || true
kextload -b com.apple.driver.AppleCameraInterface 2>/dev/null || true
kextload /System/Library/Extensions/AppleCameraInterface.kext 2>/dev/null || true
rm -f /var/tmp/.camera_blocked 2>/dev/null || true
if [ -f /usr/local/bin/camera-blocker/camera_blocker.py ]; then
    python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop 2>/dev/null || true
fi
rm -f /Library/LaunchDaemons/com.camerablocker.daemon.plist
rm -f /usr/local/bin/camera-blocker-*
rm -rf /usr/local/bin/camera-blocker
rm -rf /var/log/camera-blocker
rm -f /var/tmp/camera_blocker_status.txt
touch /var/tmp/camera_blocker.disabled
echo "Восстановление завершено."

