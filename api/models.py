from mongoengine import Document, StringField, IntField, FloatField, DateTimeField
import datetime

class AirQualityData(Document):
    room_name = StringField(required=True)
    temperature = FloatField(required=True)
    humidity = FloatField(required=True)
    light = IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_latest_data(cls, room_name):
        return cls.objects(room_name=room_name).order_by("-time").first()


    