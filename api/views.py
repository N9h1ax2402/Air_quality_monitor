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

    # Using One Call API which is more reliable than forecast/daily
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,  
        "lon": lon,    
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
        # Get location data
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

        # Extract data from current weather API (structure differs from forecast/daily)
        data = {
            "location": location_name, 
            "weather": weather_data["weather"][0]["description"],
            "temperature": weather_data["main"]["temp"],
            "low": weather_data["main"]["temp_min"],
            "high": weather_data["main"]["temp_max"],
            "humidity": weather_data["main"]["humidity"]  # Add humidity
        }
        return Response(data)
    
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Failed to fetch data: {str(e)}"}, status=500)

@api_view(['GET'])
def get_humidity_report(request, room_id):
    indoor_data = AirQualityData.get_latest_data(room_id)
 
    # Use current weather API instead of forecast/daily
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        # Extract humidity from the correct location in the JSON response
        outdoor_humidity = weather_data["main"]["humidity"]
        
        # Ensure indoor humidity is available
        indoor_humidity = getattr(indoor_data, 'humidity', 0)
        if indoor_humidity is None:
            indoor_humidity = 0
            
        data = {
            "room_id": room_id,
            "indoor": [{"humidity": indoor_humidity, "timestamp": indoor_data.time}],
            "outdoor": [{"humidity": outdoor_humidity, "timestamp": datetime.datetime.now().isoformat()}],
        }
        return Response(data)

    except requests.RequestException as e:
        return Response({"error": "Failed to fetch outdoor humidity", "details": str(e)}, status=500)
    except (KeyError, TypeError) as e:
        # Specific error for when the API response doesn't match expected structure
        return Response({"error": "Invalid weather API response format", "details": str(e)}, status=500)

@api_view(['GET'])
def get_temperature_report(request, room_id):
    indoor_data = AirQualityData.get_latest_data(room_id)

    # Use current weather API instead of forecast/daily
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        weather_data = response.json()

        # Extract temperature from the correct location in the JSON response
        outdoor_temperature = weather_data["main"]["temp"]
        
        # Ensure indoor temperature is available
        indoor_temperature = getattr(indoor_data, 'temperature', 0)
        if indoor_temperature is None:
            indoor_temperature = 0
            
        data = {
            "room_id": room_id,
            "indoor": [{"temperature": indoor_temperature, "timestamp": indoor_data.time}],
            "outdoor": [{"temperature": outdoor_temperature, "timestamp": datetime.datetime.now().isoformat()}],
        }
        return Response(data)

    except requests.RequestException as e:
        return Response({"error": "Failed to fetch outdoor temperature", "details": str(e)}, status=500)
    except (KeyError, TypeError) as e:
        # Specific error for when the API response doesn't match expected structure
        return Response({"error": "Invalid weather API response format", "details": str(e)}, status=500)

@api_view(['GET'])
def debug_weather_api(request):
    """Debug endpoint to examine the raw API response"""
    # Use current weather API
    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        return Response({
            "status": "success",
            "raw_response": weather_data,
            "humidity_path": weather_data.get("main", {}).get("humidity", "Not found"),
            "temperature_path": weather_data.get("main", {}).get("temp", "Not found")
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)

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

    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 44.34,  
        "lon": 10.99,   
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }


    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()

        data = {
            "room_id": room_id,
            "indoor": [{"humidity": indoor_data.humidity, "timestamp": indoor_data.time}],
            "outdoor": [{"humidity":  weather_data["main"]["humidity"], "timestamp": indoor_data.time}],
        }



    return Response(data)
@api_view(['GET'])
def get_temperature_report(request, room_id):
    indoor_data = AirQualityData.get_latest_data(room_id)

    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": 44.34,  
        "lon": 10.99,   
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }


    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()

        data = {
            "room_id": room_id,
            "indoor": [{"temperature": indoor_data.temperature, "timestamp": indoor_data.time}],
            "outdoor": [{"temperature":  weather_data["main"]["temperature"], "timestamp": indoor_data.time}],
        }



    return Response(data)

@api_view(['GET'])
def get_equipments(request, room_id):
    equipment_data_list = Equipments.get_equipment_status(room_id)
    
    if not equipment_data_list:
        return Response({"error": "No equipment found for the given room_id"}, status=404)
    
    data = []
    for eq in equipment_data_list:
        data.append({
            "id": str(eq.id),          # Convert ObjectId to string
            "name": eq.name,
            "status": eq.status,
        })

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

import paho.mqtt.client as mqtt

@api_view(['PUT'])
def perform_action(request, room_id):
    
    name = request.data.get("device")
    status = request.data.get("status")
    action = Equipments.get_action(room_id, name)
    # {"device": "Fan",  "status": "on"}
    print(f"Action: {action}")
    if not action:
        return Response({"error": "No action found for the given room_id and device_id"}, status=404)
    if name == "Fan":
        try:
            print(f"Performing action: {action.status} on device: {name} in room: {room_id}")
            mqtt_client = mqtt.Client()
            MQTT_USERNAME = "quanque_232"

            mqtt_client.username_pw_set(MQTT_USERNAME, "")
            mqtt_client.connect("mqtt.ohstem.vn", 1883, 60)
                    
            topic = f"{MQTT_USERNAME}/feeds/V4"
            print(f"Topic: {topic}")
            if not  topic:
                return Response({"error": "Invalid device ID"}, status=400)
            if status == "on":
                action.status = True
                action.msg = "Turned on"
                mqtt_client.publish(topic, 50)
            elif status == "off":
                action.status = False
                action.msg = "Turned off"
                mqtt_client.publish(topic, 0)

            Equipments.objects(room_id=room_id, name = name).update_one(
                set__status=action.status,
                set__msg=action.msg,
                upsert=True
            )

            mqtt_client.disconnect()
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    elif name == "Light":
        print("Light")
        try:
            print(f"Performing action: {action.status} on device: {name} in room: {room_id}")
            mqtt_client = mqtt.Client()
            MQTT_USERNAME = "quanque_232"

            mqtt_client.username_pw_set(MQTT_USERNAME, "")
            mqtt_client.connect("mqtt.ohstem.vn", 1883, 60)
                    
            topic = f"{MQTT_USERNAME}/feeds/V5"
            print(f"Topic: {topic}")
            if not  topic:
                return Response({"error": "Invalid device ID"}, status=400)
            if status == "on":
                action.status = True
                action.msg = "Turned on"
                mqtt_client.publish(topic, 1)
            elif status == "off":
                action.status = False
                action.msg = "Turned off"
                mqtt_client.publish(topic, 0)

            Equipments.objects(room_id=room_id, name = name).update_one(
                set__status=action.status,
                set__msg=action.msg,
                upsert=True
            )

            mqtt_client.disconnect()
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    data = {
        "status": action.status,
        "msg": action.msg,
    }
    return Response(data)



@api_view(['GET'])
def get_report_list(request, room_id):
    default_option = "7days"
    try:
        option = request.query_params.get("range")
    except:
        option = default_option
        pass

    if option == "7days":
        air_datas = AirQualityData.get_daily_averages(room_id)
    else:
        air_datas = AirQualityData.get_hours_average(room_id)
    
    data = {
        "room_id": room_id,
        "date": air_datas['date'],
        "temperature": air_datas['avg_temp'],
        "humidity": air_datas['avg_humid'],
    }

    return Response(data)
