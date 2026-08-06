# monitoring.py
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone
from .models import Device

MAX_WORKERS = 700  # 200 ta thread bir vaqtda ishlaydi

def ping_device(device):
    ip = device.ip_address
    response = os.system(f"ping -n 1 -w 800 {ip} > nul")  # Windows uchun
    is_up = (response == 0)
    if device.is_active != is_up:
        device.is_active = is_up
        device.last_checked = timezone.now()
        device.save(update_fields=['is_active', 'last_checked'])

def monitor_devices():
    while True:
        devices = list(Device.objects.all())
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(ping_device, dev) for dev in devices]
            for _ in as_completed(futures):
                pass
        print(f"[{timezone.now()}] {len(devices)} ta qurilma tekshirildi ✅")
        time.sleep(20)  # har 20 sekundda qayta
