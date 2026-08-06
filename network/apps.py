from django.apps import AppConfig
import threading

class NetworkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'network'

    def ready(self):
        from .monitoring import monitor_devices
        thread = threading.Thread(target=monitor_devices,daemon=True)
        thread.start()