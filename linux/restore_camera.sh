#!/bin/bash
set -e
if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: Требуются права root."
    exit 1
fi
systemctl stop camera-blocker 2>/dev/null || true
systemctl disable camera-blocker 2>/dev/null || true
pkill -9 -f camera_blocker.py 2>/dev/null || true
if [ -f /etc/modprobe.d/camera-blocker-blacklist.conf ]; then
    rm -f /etc/modprobe.d/camera-blocker-blacklist.conf
fi
modprobe uvcvideo 2>/dev/null || true
modprobe videodev 2>/dev/null || true
if [ -f /usr/local/bin/camera-blocker/camera_blocker.py ]; then
    python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop 2>/dev/null || true
fi
rm -f /etc/systemd/system/camera-blocker.service
systemctl daemon-reload
rm -f /usr/local/bin/camera-blocker-*
rm -rf /usr/local/bin/camera-blocker
rm -rf /var/log/camera-blocker
rm -f /var/tmp/camera_blocker_status.txt
touch /var/tmp/camera_blocker.disabled
echo "Восстановление завершено."

