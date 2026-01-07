#!/bin/bash
# Camera Blocker - Установка для Linux

set -e

echo "========================================"
echo " Camera Blocker - Установка (Linux)"
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

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    echo "Дистрибутив: $PRETTY_NAME"
else
    DISTRO="unknown"
    echo "Не удалось определить дистрибутив."
fi
echo ""

echo "Создание директорий..."
mkdir -p /usr/local/bin/camera-blocker
mkdir -p /var/log/camera-blocker
mkdir -p /etc/systemd/system

echo "Копирование файлов..."
cp camera_blocker.py /usr/local/bin/camera-blocker/
chmod +x /usr/local/bin/camera-blocker/camera_blocker.py

echo "Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "Python3 не найден. Попытка установки..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update && apt-get install -y python3
            ;;
        fedora|rhel|centos)
            dnf install -y python3 || yum install -y python3
            ;;
        arch|manjaro)
            pacman -S --noconfirm python
            ;;
        *)
            echo "Ошибка: Не удалось установить Python3 автоматически."
            exit 1
            ;;
    esac
fi

echo "Проверка lsof..."
if ! command -v lsof &> /dev/null; then
    case $DISTRO in
        ubuntu|debian)
            apt-get update && apt-get install -y lsof
            ;;
        fedora|rhel|centos)
            dnf install -y lsof || yum install -y lsof
            ;;
        arch|manjaro)
            pacman -S --noconfirm lsof
            ;;
    esac
fi

echo "Создание systemd-сервиса..."
cat > /etc/systemd/system/camera-blocker.service << 'EOF'
[Unit]
Description=Camera Blocker Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/camera-blocker/camera_blocker.py --start
ExecStop=/usr/bin/python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop
Restart=always
RestartSec=10
StandardOutput=append:/var/log/camera-blocker/stdout.log
StandardError=append:/var/log/camera-blocker/stderr.log

[Install]
WantedBy=multi-user.target
EOF

chmod 644 /etc/systemd/system/camera-blocker.service

echo "Создание команд управления..."
cat > /usr/local/bin/camera-blocker-start << 'EOF'
#!/bin/bash
sudo systemctl start camera-blocker
echo "Блокировка запущена."
EOF

cat > /usr/local/bin/camera-blocker-stop << 'EOF'
#!/bin/bash
sudo systemctl stop camera-blocker
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop
echo "Блокировка остановлена."
EOF

cat > /usr/local/bin/camera-blocker-status << 'EOF'
#!/bin/bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --status
echo ""
echo "Статус сервиса:"
sudo systemctl status camera-blocker --no-pager
EOF

cat > /usr/local/bin/camera-blocker-enable << 'EOF'
#!/bin/bash
sudo systemctl enable camera-blocker
echo "Автозапуск включён."
EOF

cat > /usr/local/bin/camera-blocker-disable << 'EOF'
#!/bin/bash
sudo systemctl disable camera-blocker
echo "Автозапуск отключён."
EOF

chmod +x /usr/local/bin/camera-blocker-*

echo "Блокировка камеры..."
python3 /usr/local/bin/camera-blocker/camera_blocker.py --block

echo "Настройка автозапуска..."
systemctl daemon-reload
systemctl enable camera-blocker
systemctl start camera-blocker 2>/dev/null || true

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

