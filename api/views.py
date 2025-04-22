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
    endpoints = [
        ("Real-time Air Data (room name)", "/api/air-quality/test-room/"),
        ("Weather Info", "/api/main/weather"),
        ("Room List", "/api/main/room"),
        ("Equipments (room_id)", "/api/rooms/1/equipments"),
        ("Air Parameters (room_id)", "/api/rooms/1/parameters"),
        ("Humidity Report (room_id)", "/api/rooms/1/humidity"),
        ("Temperature Report (room_id)", "/api/rooms/1/temperature"),
        ("Perform Action (room_id)", "/api/rooms/1/actions"),
    ]

    html = """
    <html>
    <head>
        <title>Air Quality API</title>
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
        <h1>🚀 Welcome to the Air Quality API</h1>
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
def get_realtime_data(request, room_name):
    latest_data = AirQualityData.get_latest_data(room_name)
    if latest_data:
        data = {
            "room_name": latest_data.room_name,
            "temperature": latest_data.temperature,
            "humidity": latest_data.humidity,
            "light": latest_data.light,
            "time" : latest_data.time
        }
        AirQualityHistory(data).save() # lưu dữ liệu vào collection lịch sử

        return Response(data)
    return Response({"error": "No data available"}, status=404)


def list_routes(request):
    urls = [str(pattern) for pattern in get_resolver().url_patterns]
    return JsonResponse({"routes": urls})

@api_view(['GET'])
def get_weather_info(request):

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
            "location": "test", 
            "weather": weather_data["list"][0]["weather"][0]["description"],
            "temperature": weather_data["list"][0]["temp"]["day"],
            "low": weather_data["list"][0]["temp"]["min"],
            "high": weather_data["list"][0]["temp"]["max"]
        }
        return Response(data)
    else:
        return JsonResponse({"error": "Failed to fetch weather data"}, status=response.status_code)

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
    name = Rooms.get_room(room_id)
    indoor_data = AirQualityData.objects(name).order_by("-time").first()

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
    name = Rooms.get_room(room_id)
    indoor_data = AirQualityData.objects(name).order_by("-time").first()

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

@api_view(['GET'])
def get_air_parameters(request, room_id):
    name = Rooms.get_room(room_id)
  
    air_data = AirQualityData.get_latest_data(name)
    
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


    
