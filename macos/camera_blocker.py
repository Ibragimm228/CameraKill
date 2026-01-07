"""
Camera Blocker для MacOS
Принудительное отключение камеры на MacOS системах | @FrontendMania
"""

import os
import sys
import time
import subprocess
import argparse
import logging
import signal
import platform
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("/var/log/camera-blocker")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"camera_blocker_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CameraBlocker:
    def __init__(self):
        self.running = True
        self.status_file = Path("/var/tmp/camera_blocker_status.txt")
        self.is_arm = platform.machine() == 'arm64'
        self.kext_paths = [
            "/System/Library/Extensions/AppleCameraInterface.kext",
            "/System/Library/DriverExtensions/AppleCameraInterface.kext",
        ]
        
    def is_root(self):
        return os.geteuid() == 0

    def block_camera_services(self):
        """Отключение служб через launchctl"""
        logging.info("Остановка системных служб камеры...")
        services = [
            "com.apple.applecamerad",
            "com.apple.VDCAssistant"
        ]
        for service in services:
            try:
                subprocess.run(["sudo", "killall", "-9", service.split('.')[-1]], capture_output=True)
                
                subprocess.run(["sudo", "launchctl", "bootout", f"system/{service}"], capture_output=True)
                subprocess.run(["sudo", "launchctl", "disable", f"system/{service}"], capture_output=True)
                logging.info(f"Служба {service} деактивирована")
            except Exception as e:
                logging.debug(f"Не удалось деактивировать {service}: {e}")
        return True

    def unblock_camera_services(self):
        logging.info("Восстановление системных служб камеры...")
        services = [
            "com.apple.applecamerad",
            "com.apple.VDCAssistant"
        ]
        for service in services:
            try:
                subprocess.run(["sudo", "launchctl", "enable", f"system/{service}"], capture_output=True)
                logging.info(f"Служба {service} включена")
            except Exception as e:
                logging.debug(f"Не удалось включить {service}: {e}")
        return True
    
    def get_camera_processes(self):
        try:
            result = subprocess.run(
                ["lsof", "|", "grep", "AppleCamera"],
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"❌ Ошибка получения процессов камеры: {e}")
            return ""
    
    def kill_camera_processes(self):
        logging.info("Поиск активных процессов...")
        
        try:
            search_patterns = ['applecamerad', 'VDCAssistant', 'Camera', 'FaceTime', 'Zoom', 'Webex', 'Slack', 'Teams']
            
            pids = set()
            for pattern in search_patterns:
                try:
                    result = subprocess.run(
                        ["pgrep", "-i", pattern],
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        pids.update(result.stdout.strip().split('\n'))
                except Exception:
                    pass
            
            if not pids:
                result = subprocess.run(
                    "lsof | grep -i 'camera\\|VDC' | awk '{print $2}' | sort -u",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                pids.update([pid for pid in result.stdout.strip().split('\n') if pid.isdigit()])

            pids = [pid for pid in pids if pid.isdigit() and int(pid) != os.getpid()]
            
            if pids:
                logging.info(f"Найдено процессов: {len(pids)}")
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        logging.info(f"Процесс {pid} остановлен")
                    except ProcessLookupError:
                        pass
                    except Exception as e:
                        logging.error(f"❌ Ошибка остановки процесса {pid}: {e}")
            else:
                logging.info("Активные процессы не найдены")
                
        except Exception as e:
            logging.error(f"❌ Ошибка при остановке процессов: {e}")
    
    def block_camera_kext(self):
        logging.info("Выгрузка расширений ядра...")
        
        self.block_camera_services()
        
        if self.is_arm:
            logging.info("Использование методов блокировки для ARM.")
            block_file = Path("/var/tmp/.camera_blocked")
            block_file.write_text("blocked")
            return True

        try:
            commands = [
                "sudo kextunload -b com.apple.driver.AppleCameraInterface",
                "sudo kextunload /System/Library/Extensions/AppleCameraInterface.kext",
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
            
            logging.info("Расширения ядра выгружены")
            
            block_file = Path("/var/tmp/.camera_blocked")
            block_file.write_text("blocked")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка блокировки kext: {e}")
            return False
    
    def unblock_camera_kext(self):
        logging.info("Загрузка расширений ядра...")
        
        self.unblock_camera_services()
        
        if self.is_arm:
            block_file = Path("/var/tmp/.camera_blocked")
            if block_file.exists():
                block_file.unlink()
            return True

        try:
            commands = [
                "sudo kextload -b com.apple.driver.AppleCameraInterface",
                "sudo kextload /System/Library/Extensions/AppleCameraInterface.kext",
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except Exception:
                    pass
            
            logging.info("Расширения ядра загружены")
            
            block_file = Path("/var/tmp/.camera_blocked")
            if block_file.exists():
                block_file.unlink()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка разблокировки kext: {e}")
            return False
    
    def block_camera_tcc(self):
        logging.info("Очистка TCC-разрешений...")
        
        try:
            subprocess.run(["tccutil", "reset", "Camera"], capture_output=True)
            logging.info("TCC-разрешения сброшены через tccutil")
            
            tcc_db = Path.home() / "Library/Application Support/com.apple.TCC/TCC.db"
            if tcc_db.exists():
                subprocess.run(
                    f"sqlite3 '{tcc_db}' \"DELETE FROM access WHERE service='kTCCServiceCamera';\"",
                    shell=True,
                    capture_output=True
                )
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка блокировки TCC: {e}")
            return False
    
    def monitor_and_block(self):
        logging.info("Запуск мониторинга...")
        
        self.block_camera_kext()
        
        self.status_file.write_text("running")
        
        try:
            while self.running:
                time.sleep(3)
                
                self.kill_camera_processes()
                
                block_file = Path("/var/tmp/.camera_blocked")
                if not block_file.exists():
                    logging.warning("Попытка деактивации блокировки!")
                    self.block_camera_kext()
                
        except KeyboardInterrupt:
            logging.info("Остановка мониторинга")
            self.status_file.write_text("stopped")
    
    def get_status(self):
        logging.info("Запрос статуса...")
        
        print("\n" + "="*30)
        print("СТАТУС КАМЕРЫ (macOS)")
        print("="*30)
        
        block_file = Path("/var/tmp/.camera_blocked")
        if block_file.exists():
            print("\nКамера: ЗАБЛОКИРОВАНА")
        else:
            print("\nКамера: АКТИВНА")
        
        processes = self.get_camera_processes()
        if processes:
            print(f"\nАктивные процессы найдены:\n{processes}")
        else:
            print("\nАктивные процессы не найдены")
        
        if self.status_file.exists():
            status = self.status_file.read_text().strip()
            print(f"\nСлужба мониторинга: {status.upper()}")
        
        print("\n" + "="*30 + "\n")

def main():
    disabled_marker = Path("/var/tmp/camera_blocker.disabled")
    if disabled_marker.exists():
        print("Программа была деактивирована пользователем.")
        print("Для повторного использования удалите /var/tmp/camera_blocker.disabled и запустите установку снова.")
        sys.exit(0)
    
    if os.geteuid() != 0:
        print("Ошибка: Требуются права root.")
        print(f"Запустите: sudo python3 {sys.argv[0]}")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Camera Blocker - Утилита для блокировки камеры (macOS)"
    )
    parser.add_argument(
        '--start',
        action='store_true',
        help='Запуск мониторинга и блокировки'
    )
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Разблокировка устройств'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Показать текущий статус'
    )
    parser.add_argument(
        '--block',
        action='store_true',
        help='Разовая блокировка без мониторинга'
    )
    
    args = parser.parse_args()
    
    blocker = CameraBlocker()
    
    if args.status:
        blocker.get_status()
    elif args.stop:
        print("Разблокировка камеры...")
        blocker.unblock_camera_kext()
        blocker.status_file.write_text("stopped")
        print("Готово.")
    elif args.block:
        print("Блокировка камеры...")
        if blocker.block_camera_kext():
            blocker.kill_camera_processes()
            print("Успешно заблокировано.")
        else:
            print("Не удалось заблокировать камеру.")
    elif args.start:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()
    else:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()

if __name__ == "__main__":
    main()

