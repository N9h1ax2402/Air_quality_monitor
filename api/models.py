from mongoengine import Document, StringField, IntField, FloatField, BooleanField, DateTimeField
import datetime

class AirQualityData(Document):
    room_id = IntField(required=True)
    temperature = FloatField(required=True)
    humidity = FloatField(required=True)
    light = IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_latest_data(cls, room_id):
        return cls.objects(room_id=room_id).order_by("-time").first()
    
class Equipments(Document):
    id = StringField(primary_key=True, required=True)
    name = StringField(required=True)
    status = BooleanField(required=True)
    room_id = IntField(required=True)

    @classmethod
    def get_equipment_status(cls, room_id):
        return cls.objects(room_id=room_id).first()
    
class Rooms(Document):
    id = IntField(primary_key=True, required=True)
    name = StringField(required=True)
    device = IntField(required=True)

    @classmethod
    def get_room_list(cls):
        return cls.objects().order_by("-last_updated")
    
    @classmethod
    def get_room(cls, room_id):
        room = cls.objects(id=room_id).first()
        return room 
    
class Actions(Document):
    room_id = IntField( required=True)
    device_id = IntField(required=True)
    status = BooleanField(required=True)
    msg = StringField(required=True)

    @classmethod
    def get_action(cls, room_id, device_id):
        return cls.objects(room_id=room_id, device_id=device_id).first()


    