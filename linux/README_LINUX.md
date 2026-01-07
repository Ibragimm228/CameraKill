# Camera Blocker для Linux

Инструкция по установке и управлению блокировщиком камеры в Linux-системах.

## Быстрая установка

1. Перейдите в папку с Linux-скриптами:
   ```bash
   cd linux
   ```
2. Разрешите выполнение скриптов:
   ```bash
   chmod +x *.sh *.py
   ```
3. Запустите инсталлятор:
   ```bash
   sudo ./install.sh
   ```

После этого камера будет заблокирована, а в системе появится сервис для автозагрузки.

## Управление

После установки в системе появятся удобные алиасы (короткие команды):

*   `camera-blocker-status` — проверить, заблокирована ли камера.
*   `camera-blocker-start` — включить блокировку и мониторинг.
*   `camera-blocker-stop` — временно разрешить использование камеры.
*   `camera-blocker-enable` — включить автозапуск при старте системы.
*   `camera-blocker-disable` — отключить автозапуск.

### Работа через systemctl
Если вы предпочитаете стандартные средства `systemd`:
```bash
sudo systemctl status camera-blocker
sudo systemctl start camera-blocker
sudo systemctl stop camera-blocker
```

## Как это работает
1. Скрипт создает файл `/etc/modprobe.d/camera-blocker-blacklist.conf`, запрещающий загрузку модулей камеры.
2. Выгружает активные модули (uvcvideo и др.).
3. Запускает фоновый процесс, который каждые несколько секунд проверяет, не появилась ли камера в системе снова.

## Удаление
Чтобы полностью удалить программу и вернуть все настройки в исходное состояние:
```bash
sudo ./uninstall.sh
```

## Расположение файлов
*   **Исполняемые файлы:** `/usr/local/bin/camera-blocker/`
*   **Логи:** `/var/log/camera-blocker/`
*   **Сервис:** `/etc/systemd/system/camera-blocker.service`

## Возможные проблемы
*   **Камера не блокируется:** Проверьте, запущен ли скрипт от root (sudo). Посмотрите логи: `cat /var/log/camera-blocker/stdout.log`.
*   **Нужно срочно включить камеру:** Выполните `camera-blocker-stop` или просто `sudo modprobe uvcvideo`.

---
Берегите свою приватность!

