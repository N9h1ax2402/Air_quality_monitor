import datetime
import json
from django.http import HttpResponse
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import *
from django.urls import get_resolver
from django.http import JsonResponse
from history.models import AirQualityHistory
import requests



from django.http import HttpResponse

def api_root(request):
    # Dynamically get all room IDs from the database
    rooms = Rooms.objects.all()  # Assuming you have a Room model
    
    # Basic endpoints
    endpoints = [
        ("Weather Info", "/api/main/weather"),
        ("Room List", "/api/main/room"),
    ]
    
    # Add room-specific endpoints for each room
    for room in rooms:
        endpoints.append((f"Equipments for {room.name}", f"/api/rooms/{room.id}/equipments"))
        endpoints.append((f"Air Parameters for {room.name}", f"/api/rooms/{room.id}/parameters"))
        endpoints.append((f"Humidity Report for {room.name}", f"/api/rooms/{room.id}/humidity"))
        endpoints.append((f"Temperature Report for {room.name}", f"/api/rooms/{room.id}/temperature"))
    
    # Add the equipment update endpoint as an example
    endpoints.append(("View Equipment Update (Example)", "/api/equipments/eq1/update/"))
    
    # Generate HTML
    html = """
    <html>
    <head>
        <title>Smart Home API</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; padding: 40px; }
            h1 { color: #333; }
            .button-container { margin-top: 30px; display: flex; flex-wrap: wrap; gap: 12px; }
            .button {
                background-color: #007BFF;
                color: white;
                padding: 12px 18px;
                text-decoration: none;
                border-radius: 6px;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            .button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <h1>🏠 Welcome to the Smart Home API</h1>
        <p>Select an endpoint to explore:</p>
        <div class="button-container">
    """

    for label, url in endpoints:
        html += f'<a class="button" href="{url}">{label}</a>\n'

    html += """
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_realtime_data(request, room_id):
    latest_data = AirQualityData.get_latest_data(room_id)
    if latest_data:
        data = {
            "room_name": latest_data.room_id,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "light": latest_data.light,
            "time" : latest_data.time
        }
        # AirQualityHistory(data).save() # lưu dữ liệu vào collection lịch sử

        return Response(data)
    return Response({"error": "No data available"}, status=404)


def list_routes(request):
    urls = [str(pattern) for pattern in get_resolver().url_patterns]
    return JsonResponse({"routes": urls})

@api_view(['GET'])
def get_weather_info(request):

    lat = request.query_params.get('lat', '44.34')  # Default if not provided
    lon = request.query_params.get('lon', '10.99')  # Default if not provided

    api_url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": lat,  
        "lon": lon,  
        "cnt": 7,      
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }

    geo_url = "https://api.openweathermap.org/geo/1.0/reverse"
    geo_params = {
        "lat": lat,
        "lon": lon,
        "limit": 1,
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5"
    }

    try:

        geo_response = requests.get(geo_url, params=geo_params)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        location_name = "Unknown Location"
        if geo_data and len(geo_data) > 0:
            city = geo_data[0].get("name", "")
            country = geo_data[0].get("country", "")
            location_name = f"{city}, {country}" if city else "Unknown Location"
        
        # Get weather data
        weather_response = requests.get(api_url, params=params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        data = {
            "location": location_name, 
            "weather": weather_data["list"][0]["weather"][0]["description"],
            "temperature": weather_data["list"][0]["temp"]["day"],
            "low": weather_data["list"][0]["temp"]["min"],
            "high": weather_data["list"][0]["temp"]["max"]
        }
        return Response(data)
    
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Failed to fetch data: {str(e)}"}, status=500)

@api_view(['GET'])
def get_room_list(request):
    room_list = Rooms.get_room_list()

    data = [{
        "id" : room_list.id,
        "name" : room_list.name,
        "device" : room_list.device,
    }
        for room_list in room_list
    ]

    return Response(data)

@api_view(['GET'])
def get_humidity_report(request, room_id):
    indoor_data = AirQualityData.get_latest_data(room_id)

    api_url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "cnt": 7,      
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }


    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()

        data = {
            "room_id": room_id,
            "indoor": [{"humidity": indoor_data.humidity, "timestamp": indoor_data.time}],
            "outdoor": [{"humidity": weather_data["list"][0]["humidity"], "timestamp": indoor_data.time}],
        }



    return Response(data)
@api_view(['GET'])
def get_temperature_report(request, room_id):
    indoor_data = AirQualityData.get_latest_data(room_id)

    api_url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "cnt": 7,      
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }


    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()

        data = {
            "room_id": room_id,
            "indoor": [{"temperature": indoor_data.temperature, "timestamp": indoor_data.time}],
            "outdoor": [{"temperature": weather_data["list"][0]["temp"]["day"], "timestamp": indoor_data.time}],
        }



    return Response(data)

@api_view(['GET'])
def get_equipments(request, room_id):
    equipment_data = Equipments.get_equipment_status(room_id)
    
    if not equipment_data:
        return Response({"error": "No equipment found for the given room_id"}, status=404)
    
    data = {
        "id": equipment_data.id,
        "name": equipment_data.name,
        "status": equipment_data.status,
    }
    return Response(data)

@api_view(['PUT'])
def update_equipment_status(request, equipment_id):
    try:
        equipment = Equipments.objects.get(id=equipment_id)
        
        # Get the new status from request data
        new_status = request.data.get('status')
        
        # Update the status
        equipment.status = new_status
        equipment.save()
        
        data = {
            "id": equipment.id,
            "name": equipment.name,
            "status": equipment.status,
        }
        return Response(data)
    except Equipments.DoesNotExist:
        return Response({"error": "Equipment not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET'])
def get_air_parameters(request, room_id):
    
  
    air_data = AirQualityData.get_latest_data(room_id)
    
    data = {
        "room_id": room_id,
        "temperature": air_data.temperature,
        "humidity": air_data.humidity,
    }
    return Response(data)

@api_view(['PUT'])
def perform_action(request, room_id):
    
    device_id = request.data.get("device")
    action = Actions.get_action(room_id, device_id)

    if action:
        data ={
            "status": action.status,
            "msg": action.msg,
        }
        return Response(data)
    return Response({"error": "No action found for the given room_id and device_id"}, status=404)


    
