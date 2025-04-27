# api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import AirQualityData

class AirQualityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Attempting to connect to WebSocket")
        self.room_id = self.scope['url_route']['kwargs']['room_id']  # Changed from room_name to room_id
        self.room_group_name = f"air_quality_{self.room_id}"  # Updated to use room_id
        print(f"Room ID: {self.room_id}, Group name: {self.room_group_name}")

        # Add the client to the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        print("Added to channel layer group")

        await self.accept()
        print("WebSocket connection accepted")

        # Fetch the latest data
        try:
            latest_data = AirQualityData.get_latest_data(self.room_id)  # Updated to pass room_id
            print(f"Latest data for room_id {self.room_id}: {latest_data}")
            if latest_data:
                await self.send(text_data=json.dumps({
                    "room": latest_data.room_id,
                    "temperature": latest_data.temperature,
                    "humidity": latest_data.humidity,
                    "light": latest_data.light,
                    "time": latest_data.time.isoformat()
                }))
                print("Sent latest data to client")
            else:
                print(f"No data found for room_id: {self.room_id}")
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            raise

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print("Disconnected from WebSocket")

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")

        if message == "request_update":
            try:
                latest_data = AirQualityData.get_latest_data(self.room_id)  
                if latest_data:
                    await self.send(text_data=json.dumps({
                        "room": latest_data.room_id,
                        "temperature": latest_data.temperature,
                        "humidity": latest_data.humidity,
                        "light": latest_data.light,
                        "time": latest_data.time.isoformat()
                    }))
                    print("Sent updated data on request")
            except Exception as e:
                print(f"Error handling request_update: {str(e)}")

    async def air_quality_message(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps(data))
        print("Sent group message to client")
        