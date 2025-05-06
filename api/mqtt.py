# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt
import time
import json

import datetime
from mongoengine.queryset import Q
import os
import django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'air_quality_monitor.settings')
django.setup()

from api.models import AirQualityData

MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "quanque_232"
MQTT_PASSWORD = ""
MQTT_TOPIC_PUB = [MQTT_USERNAME + "/feeds/V1", MQTT_USERNAME + "/feeds/V2", MQTT_USERNAME + "/feeds/V3"]
MQTT_TOPIC_SUB = [MQTT_USERNAME + "/feeds/V1", 
                  MQTT_USERNAME + "/feeds/V2", 
                  MQTT_USERNAME + "/feeds/V3" ]


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
    global temperature, humidity, aqi
    payload = message.payload.decode("utf-8")
    topic = message.topic

    try:
        data = json.loads(payload)
        room_id = int(1)
        if topic.endswith("V1"):
            data_store["humidity"] = float(data)
        elif topic.endswith("V2"):
            data_store["temperature"] = float(data)
        else:
            data_store["light"] = int(data)
        if all(data_store[key] is not None for key in ["temperature", "humidity", "light"]):
            
            result = AirQualityData.objects(Q(room_id=room_id)).update_one(
                set__temperature=data_store["temperature"],
                set__humidity=data_store["humidity"],
                set__light=data_store["light"],
                set__time=datetime.datetime.now(datetime.UTC),
                upsert=True  # Nếu không có dữ liệu, tạo mới
            )

            print(f"Temperature: {data_store['temperature']}°C, Humidity: {data_store['humidity']}%, Light: {data_store['light']}%")
            print(result)
    except json.JSONDecodeError:
        print("Error: Received invalid JSON format")

mqttClient = mqtt.Client()
mqttClient.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqttClient.connect(MQTT_SERVER, int(MQTT_PORT), 60)

mqttClient.on_connect = mqtt_connected
mqttClient.on_subscribe = mqtt_subscribed
mqttClient.on_message = mqtt_recv_message

mqttClient.loop_start()

while True:
    time.sleep(5)