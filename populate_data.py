from mongoengine import connect
from api.models import Rooms, Equipments, AirQualityData, Actions
from datetime import datetime, timedelta

# Connect to your MongoDB (adjust if needed)
connect(
    db='air_quality_monitor',
    host='localhost',
    port=27017
)

# Insert sample room
room = Rooms(id=1, name="Living Room", device=3)
room.save()

# Insert another room
AirQualityData(room_id="1", time=datetime.now() - timedelta(minutes=30), temperature=40.5, humidity=30, light=15).save()
AirQualityData(room_id="2", time=datetime.now() - timedelta(minutes=30), temperature=38.5, humidity=50, light=0).save()

AirQualityData(room_id="1", time=datetime.now() - timedelta(days=7), temperature=30, humidity=30, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=6), temperature=34, humidity=29, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=5), temperature=36, humidity=28, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=4), temperature=39, humidity=25, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=3), temperature=40, humidity=27, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=2), temperature=37, humidity=40, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(days=1), temperature=38, humidity=25, light=0).save()

AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=24), temperature=30, humidity=60, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=21), temperature=34, humidity=71, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=18), temperature=36, humidity=59, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=15), temperature=39, humidity=82, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=12), temperature=40, humidity=90, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=9), temperature=37, humidity=80, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=6), temperature=38, humidity=72, light=0).save()
AirQualityData(room_id="1", time=datetime.now() - timedelta(hours=3), temperature=38, humidity=60, light=0).save()

# Insert sample equipment
Equipments(id="eq1", name="Fan", status=True, room_id=1).save()
Equipments(id="eq2", name="Heater", status=False, room_id=2).save()
Equipments(id ="eq3", name="Air Purifier", status=True, room_id=1).save()


print("Sample data inserted!")
