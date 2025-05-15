from mongoengine import Document, StringField, IntField, FloatField, DateTimeField
import datetime

class AirQualityHistory(Document):
    room_id = IntField(required=True)
    temperature = FloatField(required=True)
    humidity = FloatField(required=True)
    light = IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_latest_data(cls, room_id):
        return cls.objects(room_id=room_id).order_by("-time").first()
