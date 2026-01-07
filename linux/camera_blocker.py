"""
Camera Blocker для Linux
Принудительное отключение камеры на Linux системах | @FrontendMania
"""

import os
import sys
import time
import subprocess
import argparse
import logging
import signal
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
        
        self.camera_modules = [
            'uvcvideo',
            'videodev',
            'v4l2_common',
            'videobuf2_core',
            'videobuf2_v4l2',
            'videobuf2_vmalloc',
            'videobuf2_memops',
        ]
        
        self.blacklist_file = Path("/etc/modprobe.d/camera-blocker-blacklist.conf")
        
    def is_root(self):
        return os.geteuid() == 0
    
    def find_camera_devices(self):
        devices = []
        
        try:
            result = subprocess.run(
                ["v4l2-ctl", "--list-devices"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                devices.append(("v4l2", result.stdout))
        except FileNotFoundError:
            pass
        
        video_devices = list(Path("/dev").glob("video*"))
        if video_devices:
            devices.append(("devices", [str(d) for d in video_devices]))
        
        return devices
    
    def unload_camera_modules(self):
        logging.info("Выгрузка модулей...")
        
        success = True
        for module in self.camera_modules:
            try:
                check = subprocess.run(
                    ["lsmod"],
                    capture_output=True,
                    text=True
                )
                
                if module in check.stdout:
                    logging.info(f"Выгрузка модуля: {module}")
                    result = subprocess.run(
                        ["modprobe", "-r", module],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        logging.info(f"Модуль {module} выгружен")
                    else:
                        logging.warning(f"Не удалось выгрузить {module}")
                        success = False
                        
            except Exception as e:
                logging.error(f"Ошибка выгрузки {module}: {e}")
                success = False
        
        return success
    
    def load_camera_modules(self):
        logging.info("Загрузка модулей...")
        
        success = True
        for module in ['uvcvideo']:
            try:
                logging.info(f"Загрузка модуля: {module}")
                result = subprocess.run(
                    ["modprobe", module],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logging.info(f"Модуль {module} загружен")
                else:
                    logging.warning(f"Не удалось загрузить {module}")
                    success = False
                    
            except Exception as e:
                logging.error(f"Ошибка загрузки {module}: {e}")
                success = False
        
        return success
    
    def create_blacklist(self):
        logging.info("Создание blacklist-файла...")
        
        try:
            with open(self.blacklist_file, 'w') as f:
                f.write("# Camera Blocker - Blacklist\n")
                f.write("# Prevents camera modules from loading\n\n")
                
                for module in self.camera_modules:
                    f.write(f"blacklist {module}\n")
                    f.write(f"install {module} /bin/false\n")
            
            logging.info("Blacklist-файл создан. Изменения вступят в силу после перезагрузки.")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка создания blacklist: {e}")
            return False
    
    def remove_blacklist(self):
        logging.info("Удаление blacklist-файла...")
        
        try:
            if self.blacklist_file.exists():
                self.blacklist_file.unlink()
                logging.info("Blacklist-файл удалён. Изменения вступят в силу после перезагрузки.")
            else:
                logging.info("Blacklist-файл не найден")
            
            return True
            
        except Exception as e:
            logging.error(f"Ошибка удаления blacklist: {e}")
            return False
    
    def kill_camera_processes(self):
        logging.info("Поиск активных процессов...")
        
        try:
            result = subprocess.run(
                "lsof /dev/video* 2>/dev/null | awk 'NR>1 {print $2}' | sort -u",
                shell=True,
                capture_output=True,
                text=True
            )
            
            pids = result.stdout.strip().split('\n')
            pids = [pid for pid in pids if pid.isdigit()]
            
            if pids:
                logging.info(f"Найдено процессов: {len(pids)}")
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        logging.info(f"Процесс {pid} остановлен")
                    except ProcessLookupError:
                        pass
                    except Exception as e:
                        logging.error(f"Ошибка остановки {pid}: {e}")
            else:
                logging.info("Активные процессы не найдены")
                
        except Exception as e:
            logging.error(f"Ошибка при поиске процессов: {e}")
    
    def monitor_and_block(self):
        logging.info("Запуск мониторинга...")
        
        self.create_blacklist()
        self.unload_camera_modules()
        self.status_file.write_text("running")
        
        try:
            while self.running:
                time.sleep(3)
                self.kill_camera_processes()
                
                check = subprocess.run(
                    ["lsmod"],
                    capture_output=True,
                    text=True
                )
                
                for module in self.camera_modules:
                    if module in check.stdout:
                        logging.warning(f"Попытка загрузки модуля: {module}")
                        subprocess.run(
                            ["modprobe", "-r", module],
                            capture_output=True
                        )
                
        except KeyboardInterrupt:
            logging.info("Остановка мониторинга")
            self.status_file.write_text("stopped")
    
    def get_status(self):
        logging.info("Запрос статуса...")
        
        print("\n" + "="*30)
        print("СТАТУС КАМЕРЫ (Linux)")
        print("="*30)
        
        check = subprocess.run(
            ["lsmod"],
            capture_output=True,
            text=True
        )
        
        modules_loaded = []
        for module in self.camera_modules:
            if module in check.stdout:
                modules_loaded.append(module)
        
        if modules_loaded:
            print("\nКамера: АКТИВНА")
            print(f"Загружено модулей: {len(modules_loaded)}")
            for module in modules_loaded:
                print(f"  - {module}")
        else:
            print("\nКамера: ЗАБЛОКИРОВАНА")
        
        video_devices = list(Path("/dev").glob("video*"))
        if video_devices:
            print(f"Найдено устройств: {len(video_devices)}")
            for device in video_devices:
                print(f"  - {device}")
        
        if self.blacklist_file.exists():
            print("Blacklist: АКТИВЕН")
        
        if self.status_file.exists():
            status = self.status_file.read_text().strip()
            print(f"Служба мониторинга: {status.upper()}")
        
        print("\n" + "="*30 + "\n")

def main():
    disabled_marker = Path("/var/tmp/camera_blocker.disabled")
    if disabled_marker.exists():
        print("Программа деактивирована.")
        print("Для повторного использования удалите /var/tmp/camera_blocker.disabled и запустите установку снова.")
        sys.exit(0)
    
    if os.geteuid() != 0:
        print("Ошибка: Требуются права root.")
        print(f"Запустите: sudo python3 {sys.argv[0]}")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Camera Blocker - Утилита для блокировки камеры (Linux)"
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
        blocker.remove_blacklist()
        blocker.load_camera_modules()
        blocker.status_file.write_text("stopped")
        print("Готово. (Может потребоваться перезагрузка)")
    elif args.block:
        print("Блокировка камеры...")
        blocker.create_blacklist()
        if blocker.unload_camera_modules():
            blocker.kill_camera_processes()
            print("Успешно заблокировано.")
        else:
            print("Некоторые модули не удалось выгрузить.")
    elif args.start:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()
    else:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()

if __name__ == "__main__":
    main()

