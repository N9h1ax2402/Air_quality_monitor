from django.apps import AppConfig
import threading

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        print("Starting MQTT service...")
        from api.mqtt import run_mqtt_client
        mqtt_thread = threading.Thread(target=run_mqtt_client)
        mqtt_thread.daemon = True
        mqtt_thread.start()