from mongoengine import connect
from api.models import Rooms, Equipments

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
Rooms(id=2, name="Master Bedroom", device=2).save()

# Insert sample equipment
Equipments(id="eq1", name="Fan", status=True, room_id=1).save()
Equipments(id="eq2", name="Heater", status=False, room_id=2).save()

print("Sample data inserted!")
