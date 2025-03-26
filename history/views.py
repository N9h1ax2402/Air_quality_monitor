from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import AirQualityHistory
from .serializers import AirQualityHistorySerializer

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_realtime_data(request, room_name):
    latest_data = AirQualityHistory.get_latest_data(room_name)
    
    if latest_data:
        serializer = AirQualityHistorySerializer(latest_data)
        return Response(serializer.data)
    
    return Response({"error": "No data available"}, status=404)
