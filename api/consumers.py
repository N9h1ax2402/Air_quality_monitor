import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import AirQualityData

class AirQualityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"air_quality_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        latest_data = AirQualityData.get_latest_data(self.room_name)
        if latest_data:
            await self.send(text_data=json.dumps({
                "room": latest_data.room,
                "temperature": latest_data.temperature,
                "humidity": latest_data.humidity,
                "light": latest_data.light,
                "time": latest_data.time.isoformat()
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data): pass

    async def send(self, event):
        await self.send(text_data=json.dumps(event["data"]))