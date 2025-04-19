from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import *
from .serializers import AirQualityHistorySerializer
import requests

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_history_data(request, room_name):
    report_type = request.GET.get('type')

    api_url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    params = {
        "lat": 44.34,  
        "lon": 10.99,  
        "cnt": 7,      
        "appid": "1da4773d93ef53ddadee33b32b8a5fd5",  
        "units": "metric"  
    }

    indoor_data = AirQualityHistory.objects(room_name=room_name).order_by("-time").first()

    response = requests.get(api_url, params=params)
    weather_data = response.json()

    if report_type == "temperature":
        data = {
            "last_updated" : indoor_data.time,
            "data" : [
                {
                    "type": report_type,
                    "indoor": indoor_data.temperature,
                    "outdoor": weather_data["list"][0]["temp"]["day"],
                    "timestamp": indoor_data.time
                }
            ]
        }
        return Response(data)
    elif report_type == "humidity":
        data = {
            "last_updated" : indoor_data.time,
            "data" : [
                {
                    "type": report_type,
                    "indoor": indoor_data.humidity,
                    "outdoor": weather_data["list"][0]["humidity"],
                    "timestamp": indoor_data.time
                }
            ]
        }
        return Response(data)
