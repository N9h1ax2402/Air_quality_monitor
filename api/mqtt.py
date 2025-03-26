# pip install paho-mqtt==1.6.1
import paho.mqtt.client as mqtt
import time
import json
from .models import AirQualityData
import datetime
from mongoengine.queryset import Q

MQTT_SERVER = "mqtt.ohstem.vn"
MQTT_PORT = 1883
MQTT_USERNAME = "nghia123"
MQTT_PASSWORD = ""
MQTT_TOPIC_SUB = MQTT_USERNAME + "/feeds/V1"


temperature = None
humidity = None
light = None

def mqtt_connected(client, userdata, flags, rc):
    print("Connected successfully!!")
    client.subscribe(MQTT_TOPIC_SUB)

def mqtt_subscribed(client, userdata, mid, granted_qos):
    print("Subscribed to Topic!!!")

def mqtt_recv_message(client, userdata, message):
    global temperature, humidity, aqi
    payload = message.payload.decode("utf-8")
    print("Received message:", payload)

    try:
        data = json.loads(payload)
        room = data.get("Room")
        temperature = data.get("Temperature")
        humidity = data.get("Humidity")
        light = data.get("Light")

        AirQualityData.objects(Q(room_name=room)).update_one(
            set__temperature=temperature,
            set__humidity=humidity,
            set__light=light,
            set__time=datetime.datetime.now(datetime.UTC),
            upsert=True  # Nếu không có dữ liệu, tạo mới
        )

        print(f"Temperature: {temperature}°C, Humidity: {humidity}%, Light: {light}%")

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
