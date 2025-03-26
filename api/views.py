import datetime
import json
from django.http import HttpResponse
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import AirQualityData
from django.urls import get_resolver
from django.http import JsonResponse
from history.models import AirQualityHistory

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

def homepage(request):
    return HttpResponse("<h1>Welcome to the Air Quality Monitoring System</h1>")

def list_routes(request):
    urls = [str(pattern) for pattern in get_resolver().url_patterns]
    return JsonResponse({"routes": urls})