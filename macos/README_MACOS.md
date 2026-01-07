# Camera Blocker для macOS

Инструкция по установке и использованию блокировщика камеры на macOS.

## Быстрая установка

1. Откройте **Терминал** (через Spotlight или в папке Программы -> Утилиты).
2. Перейдите в папку проекта:
   ```bash
   cd macos
   ```
3. Разрешите выполнение скриптов:
   ```bash
   chmod +x *.sh *.py
   ```
4. Запустите установку:
   ```bash
   sudo ./install.sh
   ```

## Управление через команды
После установки вы можете использовать в Терминале следующие команды:

*   `camera-blocker-status` — проверить состояние камеры.
*   `camera-blocker-start` — включить блокировку.
*   `camera-blocker-stop` — временно отключить блокировку.

## Как это работает
1. Скрипт выгружает расширение ядра `AppleCameraInterface`, которое отвечает за работу веб-камеры.
2. Создается системный агент (Launch Daemon), который следит, чтобы камера не включилась сама по себе.

## Особенности для новых Mac (M1/M2/M3)
На новых моделях с чипами Apple Silicon может потребоваться отключение SIP (System Integrity Protection) для управления расширениями ядра. Если скрипт выдает ошибку "Operation not permitted":
1. Загрузитесь в режим восстановления (удерживайте кнопку питания при включении).
2. Выберите «Терминал» в меню «Утилиты».
3. Введите `csrutil disable` и перезагрузитесь.
4. После установки блокировщика SIP можно включить обратно (`csrutil enable`).

## Удаление
Чтобы полностью удалить программу:
```bash
sudo ./uninstall.sh
```

## Логи
Если возникли проблемы, проверьте логи:
`cat /var/log/camera-blocker/stdout.log`

---
Берегите свою приватность!

### Удаление

```bash
sudo ./uninstall.sh
```

## 💡 Использование

### Через командные алиасы

После установки доступны удобные команды:

**Проверить статус:**
```bash
camera-blocker-status
```

**Запустить блокировку:**
```bash
camera-blocker-start
```

**Остановить блокировку:**
```bash
camera-blocker-stop
```

### Через прямой вызов

**Проверить статус:**
```bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --status
```

**Запустить блокировку с мониторингом:**
```bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --start
```

**Остановить блокировку:**
```bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --stop
```

**Просто заблокировать камеру (без мониторинга):**
```bash
sudo python3 /usr/local/bin/camera-blocker/camera_blocker.py --block
```

## ⚙️ Как это работает

1. **Управление системными службами** - отключает `applecamerad` и `VDCAssistant` через `launchctl` (особенно эффективно на Apple Silicon).
2. **Выгрузка kernel extensions** - выгружает `AppleCameraInterface.kext` (на Intel Mac).
3. **Убийство процессов** - агрессивно останавливает все процессы, использующие камеру (pgrep/lsof).
4. **Сброс TCC разрешений** - использует `tccutil reset Camera` для очистки списка разрешений приложений.
5. **Мониторинг** - каждые 3 секунды проверяет и блокирует попытки активации камеры.
6. **Launch Daemon** - автоматически запускается при загрузке системы для постоянной защиты.

## 📂 Расположение файлов

- **Программа:** `/usr/local/bin/camera-blocker/`
- **Логи:** `/var/log/camera-blocker/`
- **Launch Daemon:** `/Library/LaunchDaemons/com.camerablocker.daemon.plist`
- **Статус:** `/var/tmp/camera_blocker_status.txt`

## 🔍 Проверка работы

### Способ 1: Через команду status

```bash
camera-blocker-status
```

### Способ 2: Проверка kernel extensions

```bash
kextstat | grep -i camera
```

Если камера заблокирована, вы НЕ должны видеть AppleCameraInterface в списке.

### Способ 3: Попробуйте использовать камеру

1. Откройте FaceTime или Photo Booth
2. Если камера заблокирована, вы увидите чёрный экран или ошибку

### Способ 4: Проверка Launch Daemon

```bash
sudo launchctl list | grep camerablocker
```

## ⚠️ Возможные проблемы

### Камера не блокируется

**Решение:**
1. Убедитесь, что запустили с `sudo`
2. Проверьте логи: `cat /var/log/camera-blocker/camera_blocker_*.log`
3. На новых Mac с M1/M2 может потребоваться отключить System Integrity Protection (SIP)

### Программа не запускается

**Решение:**
1. Проверьте Python: `python3 --version`
2. Если нет, установите через Homebrew:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install python3
   ```

### Не могу включить камеру после остановки

**Решение:**
1. Запустите полное удаление:
   ```bash
   sudo ./uninstall.sh
   ```
2. Загрузите kext вручную:
   ```bash
   sudo kextload -b com.apple.driver.AppleCameraInterface
   ```
3. Перезагрузите Mac

### Ошибка "Operation not permitted"

**Решение (для новых Mac):**

На Mac с Apple Silicon (M1/M2) может потребоваться:

1. Перезагрузите в Recovery Mode (`Cmd + R` при загрузке)
2. Откройте Terminal из меню Utilities
3. Выполните:
   ```bash
   csrutil disable
   ```
4. Перезагрузитесь
5. Установите Camera Blocker
6. (Опционально) Снова включите SIP: `csrutil enable`

## 🛡️ Безопасность

- Программа не подключается к интернету
- Все операции выполняются локально
- Логи хранятся только на вашем Mac
- Исходный код открыт для проверки

## 📝 Логи

Просмотр логов:

```bash
# Логи программы
cat /var/log/camera-blocker/camera_blocker_*.log

# Stdout логи
cat /var/log/camera-blocker/stdout.log

# Stderr логи
cat /var/log/camera-blocker/stderr.log
```

Очистка логов:

```bash
sudo rm -rf /var/log/camera-blocker/*
```

## 🔄 Управление Launch Daemon

### Проверить статус

```bash
sudo launchctl list | grep camerablocker
```

### Остановить

```bash
sudo launchctl unload /Library/LaunchDaemons/com.camerablocker.daemon.plist
```

### Запустить

```bash
sudo launchctl load /Library/LaunchDaemons/com.camerablocker.daemon.plist
```

### Отключить автозапуск

```bash
sudo launchctl unload -w /Library/LaunchDaemons/com.camerablocker.daemon.plist
```

### Включить автозапуск

```bash
sudo launchctl load -w /Library/LaunchDaemons/com.camerablocker.daemon.plist
```

## 💻 Системные требования

- MacOS 10.14 (Mojave) или новее
- Python 3.6+
- Права администратора (sudo)

## 🎯 Совместимость

- ✅ MacOS Big Sur (11.x)
- ✅ MacOS Monterey (12.x)
- ✅ MacOS Ventura (13.x)
- ✅ MacOS Sonoma (14.x)
- ✅ MacOS с Apple Silicon (M1/M2/M3)

## 🆘 Получить помощь

Если программа не работает:

1. **Проверьте логи:**
   ```bash
   cat /var/log/camera-blocker/camera_blocker_*.log
   ```

2. **Запустите диагностику:**
   ```bash
   camera-blocker-status
   ```

3. **Проверьте права:**
   ```bash
   ls -la /usr/local/bin/camera-blocker/
   ```

## 🔓 Экстренная разблокировка

Если что-то пошло не так и нужно срочно разблокировать камеру:

### Способ 1: Через программу
```bash
camera-blocker-stop
```

### Способ 2: Ручная загрузка kext
```bash
sudo kextload -b com.apple.driver.AppleCameraInterface
sudo kextload /System/Library/Extensions/AppleCameraInterface.kext
```

### Способ 3: Остановка Launch Daemon
```bash
sudo launchctl unload /Library/LaunchDaemons/com.camerablocker.daemon.plist
sudo launchctl remove com.camerablocker.daemon
```

### Способ 4: Удаление программы
```bash
sudo ./uninstall.sh
```

### Способ 5: Перезагрузка
```bash
sudo reboot
```

## 🔧 Расширенные настройки

### Изменить интервал мониторинга

Отредактируйте файл `/usr/local/bin/camera-blocker/camera_blocker.py`:

```python
# Найдите строку
time.sleep(3)  # 3 секунды

# Измените на нужное значение
time.sleep(10)  # 10 секунд
```

### Добавить уведомления

Установите terminal-notifier:

```bash
brew install terminal-notifier
```

И добавьте в скрипт уведомления при блокировке.

---

**Берегите свою приватность! 🔒**

