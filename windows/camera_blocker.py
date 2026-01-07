"""
Camera Blocker для Windows
Принудительное отключение камеры на Windows системах | @FrontendMania
"""

import os
import sys
import time
import subprocess
import winreg
import ctypes
import argparse
import logging
from pathlib import Path
from datetime import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

LOG_DIR = Path("C:/ProgramData/CameraBlocker/logs")
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
        self.camera_devices = []
        self.running = True
        self.status_file = Path("C:/ProgramData/CameraBlocker/status.txt")
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
    def find_camera_devices(self):
        logging.info("Поиск устройств...")
        
        ps_command = """
        Get-PnpDevice | Where-Object {
            $_.Class -eq 'Camera' -or 
            $_.Class -eq 'Image' -or
            $_.FriendlyName -like '*camera*' -or
            $_.FriendlyName -like '*webcam*'
        } | Select-Object InstanceId, FriendlyName, Status | ConvertTo-Json
        """
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.stdout:
                import json
                devices = json.loads(result.stdout)
                
                if isinstance(devices, dict):
                    devices = [devices]
                
                self.camera_devices = devices
                logging.info(f"Найдено камер: {len(self.camera_devices)}")
                
                for device in self.camera_devices:
                    logging.info(f"Device: {device['FriendlyName']} (Status: {device['Status']})")
                    
        except Exception as e:
            logging.error(f"Ошибка при поиске устройств: {e}")
            
        return self.camera_devices
    
    def disable_camera(self, instance_id):
        ps_command = f'Disable-PnpDevice -InstanceId "{instance_id}" -Confirm:$false'
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка при отключении: {e}")
            return False
    
    def enable_camera(self, instance_id):
        ps_command = f'Enable-PnpDevice -InstanceId "{instance_id}" -Confirm:$false'
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logging.error(f"Ошибка при включении: {e}")
            return False
    
    def block_all_cameras(self):
        logging.info("Блокировка камер...")
        
        devices = self.find_camera_devices()
        
        if not devices:
            logging.warning("Устройства не найдены")
            return False
        
        success = True
        for device in devices:
            if device['Status'] != 'Error':
                logging.info(f"Отключение: {device['FriendlyName']}")
                if not self.disable_camera(device['InstanceId']):
                    success = False
                else:
                    logging.info(f"Устройство {device['FriendlyName']} отключено")
        
        return success
    
    def unblock_all_cameras(self):
        logging.info("Разблокировка камер...")
        
        devices = self.find_camera_devices()
        
        if not devices:
            logging.warning("Устройства не найдены")
            return False
        
        success = True
        for device in devices:
            if device['Status'] == 'Error':
                logging.info(f"Включение: {device['FriendlyName']}")
                if not self.enable_camera(device['InstanceId']):
                    success = False
                else:
                    logging.info(f"Устройство {device['FriendlyName']} включено")
        
        return success
    
    def monitor_and_block(self):
        logging.info("Запуск мониторинга...")
        
        self.block_all_cameras()
        self.status_file.write_text("running")
        
        try:
            while self.running:
                time.sleep(5)
                devices = self.find_camera_devices()
                
                for device in devices:
                    if device['Status'] == 'OK':
                        logging.warning(f"Обнаружена активность: {device['FriendlyName']}")
                        self.disable_camera(device['InstanceId'])
                        logging.info(f"Устройство {device['FriendlyName']} заблокировано повторно")
                        
        except KeyboardInterrupt:
            logging.info("Остановка мониторинга")
            self.status_file.write_text("stopped")
            
    def get_status(self):
        logging.info("Запрос статуса устройств...")
        
        devices = self.find_camera_devices()
        
        if not devices:
            print("\nУстройства не найдены в системе")
            return
        
        print("\n" + "="*30)
        print("СТАТУС УСТРОЙСТВ")
        print("="*30)
        
        blocked_count = 0
        active_count = 0
        
        for device in devices:
            is_blocked = device['Status'] == 'Error'
            status_text = "ЗАБЛОКИРОВАНА" if is_blocked else "АКТИВНА"
            
            if is_blocked:
                blocked_count += 1
            else:
                active_count += 1
                
            print(f"\n{device['FriendlyName']}")
            print(f"  Статус: {status_text}")
            print(f"  Instance ID: {device['InstanceId']}")
        
        print("\n" + "="*30)
        print(f"Всего: {len(devices)}")
        print(f"Заблокировано: {blocked_count}")
        print(f"Активно: {active_count}")
        print("="*30 + "\n")
        
        if self.status_file.exists():
            status = self.status_file.read_text().strip()
            if status == "running":
                print("Служба мониторинга: РАБОТАЕТ")
            else:
                print("Служба мониторинга: ОСТАНОВЛЕНА")
        else:
            print("Служба мониторинга: НЕ ЗАПУЩЕНА")
        
        print()

def main():
    disabled_marker = Path("C:/ProgramData/CameraBlocker.disabled")
    if disabled_marker.exists():
        print("Программа была деактивирована пользователем.")
        print("Для повторного использования удалите файл C:\\ProgramData\\CameraBlocker.disabled и запустите установку снова.")
        sys.exit(0)
    
    if not is_admin():
        print("Ошибка: Требуются права администратора.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Camera Blocker - Утилита для блокировки камеры"
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
        print("Разблокировка устройств...")
        blocker.unblock_all_cameras()
        blocker.status_file.write_text("stopped")
        print("Готово.")
    elif args.block:
        print("Блокировка устройств...")
        if blocker.block_all_cameras():
            print("Успешно заблокировано.")
        else:
            print("Некоторые устройства не удалось заблокировать.")
    elif args.start:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()
    else:
        print("Запуск мониторинга...")
        blocker.monitor_and_block()

if __name__ == "__main__":
    main()

