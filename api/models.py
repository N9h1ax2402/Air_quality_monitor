from mongoengine import Document, StringField, IntField, FloatField, BooleanField, DateTimeField
import datetime
from datetime import timedelta, timezone

class AirQualityData(Document):
    room_id = IntField(required=True)
    temperature = FloatField(required=True)
    humidity = FloatField(required=True)
    light = IntField(required=True)
    time = DateTimeField(default=datetime.datetime.now(datetime.UTC))

    @classmethod
    def get_latest_data(cls, room_id):
        target = cls.objects(room_id=room_id).order_by("-time").first()
        return target
    
    @classmethod
    def get_daily_averages(cls, room_id, days=7):
    
        now = datetime.datetime.now(timezone.utc)
        result = {"date": [], "avg_temp": [], "avg_humid": []}

        for i in range(days):
            day_end = now - timedelta(days=i)
            day_start = day_end - timedelta(days=1)

            records = cls.objects(
                room_id=room_id,
                time__gte=day_start,
                time__lt=day_end
            )
            avg_temp, avg_humidity = None, None

            if records:
                avg_temp = round(sum(r.temperature for r in records) / len(records), 2)
                avg_humidity = round(sum(r.humidity for r in records) / len(records), 2)
                
            result["date"].append(day_start.strftime("%d-%m"))
            result["avg_temp"].append(avg_temp)
            result["avg_humid"].append(avg_humidity)

        # Optional: reverse to show oldest first
        result["date"][0] = "today"
        return result
    
    @classmethod
    def get_hours_average(cls, room_id, last_hours=24):
    
        now = datetime.datetime.now(timezone.utc)
        result = {"date": [], "avg_temp": [], "avg_humid": []}

        for i in range(0, last_hours, 3):
            day_start = now - timedelta(hours=i)
            day_end = day_start + timedelta(hours=3)

            records = cls.objects(
                room_id=room_id,
                time__gte=day_start,
                time__lt=day_end
            )
            avg_temp, avg_humidity = None, None

            if records:
                avg_temp = sum(r.temperature for r in records) / len(records)
                avg_humidity = sum(r.humidity for r in records) / len(records)
                
            result["date"].append(str(i+3))
            result["avg_temp"].append(avg_temp)
            result["avg_humid"].append(avg_humidity)

        return result
    
class Equipments(Document):
    id = StringField(primary_key=True, required=True)
    name = StringField(required=True)
    status = BooleanField(required=True)
    room_id = IntField(required=True)
    msg = StringField(required=True)

    @classmethod
    def get_equipment_status(cls, room_id):
        return cls.objects(room_id=room_id)
    
    @classmethod
    def get_action(cls, room_id, name):
        return cls.objects(room_id=room_id, name=name).first()
    
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


    