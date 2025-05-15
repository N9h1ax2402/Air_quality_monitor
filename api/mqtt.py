# api/mqtt_service.py

import paho.mqtt.client as mqtt
import json
import datetime
import time
import threading

from mongoengine.queryset import Q
from api.models import AirQualityData
from history.models import AirQualityHistory
from air_quality_monitor.management.utils.notifications import notify_warning_clients

MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "quanque_232"
MQTT_PASSWORD = ""
MQTT_TOPIC_SUB = [
    f"{MQTT_USERNAME}/feeds/V1",
    f"{MQTT_USERNAME}/feeds/V2",
    f"{MQTT_USERNAME}/feeds/V3",
    f"{MQTT_USERNAME}/feeds/V4",
]

data_store = {
    "temperature": None,
    "humidity": None,
    "light": None
}

def mqtt_connected(client, userdata, flags, rc):
    print("Connected successfully!!")
    for topic in MQTT_TOPIC_SUB:
        client.subscribe(topic)

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    topic = message.topic

    try:
        data = json.loads(payload)
        room_id = 1  # Hardcode
        if topic.endswith("V1"):
            data_store["humidity"] = float(data)
        elif topic.endswith("V2"):
            data_store["temperature"] = float(data)
        elif topic.endswith("V3"):
            data_store["light"] = int(data)


        if all(data_store.values()):
            AirQualityData.objects(Q(room_id=room_id)).update_one(
                set__temperature=data_store["temperature"],
                set__humidity=data_store["humidity"],
                set__light=data_store["light"],
                set__time=datetime.datetime.now(datetime.UTC),
                upsert=True
            )
            print(f"Updated: Temp={data_store['temperature']}°C, Hum={data_store['humidity']}%, Light={data_store['light']}%")

            if data_store["temperature"] > 30:
                print("Temperature too high")
                notify_warning_clients(f"Temperature of room {room_id} is too high", "temperature")
            if data_store["humidity"] > 80:
                print("Humidity too high")
                notify_warning_clients(f"Humidity of room {room_id} is too high", "humidity")
            # if data_store["light"] < 100:
            #     notify_warning_clients(f"Light of room {room_id} is too low", "light")
            if data_store["light"] < 40:
                print("Light too high")
                notify_warning_clients(f"Light of room {room_id} is too high", "light")

            history_data = AirQualityHistory(
                room_id=room_id,
                temperature=data_store["temperature"],
                humidity=data_store["humidity"],
                light=data_store["light"],
                time=datetime.datetime.now(datetime.UTC)
            )
            history_data.save()

    except json.JSONDecodeError:
        print("Invalid JSON received")

def run_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = mqtt_connected
    client.on_subscribe = mqtt_subscribed
    client.on_message = mqtt_recv_message
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    
    while True:
        client.loop(timeout=1.0)
        time.sleep(5)
