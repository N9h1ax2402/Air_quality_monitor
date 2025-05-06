from django.urls import path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .consumers import AirQualityConsumer



schema_view = get_schema_view(
    openapi.Info(
        title="Air Quality Monitor API",
        default_version='v1',
        description="API documentation for your air quality monitoring system.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('ws/air-quality/<int:room_id>/', AirQualityConsumer.as_asgi(), name='air_quality_ws'),
    path('air-quality/<int:room_id>/', get_realtime_data, name='get_realtime_data'),
    path("main/weather", get_weather_info, name="get_weather_info"),
    path("main/room", get_room_list, name="get_room_list"),
    path("rooms/<int:room_id>/equipments", get_equipments, name="get_equipments"),
    path("rooms/<int:room_id>/parameters", get_air_parameters, name="get_air_parameters"),
    path("rooms/<int:room_id>/humidity", get_humidity_report, name="get_humidity_report"),
    path("rooms/<int:room_id>/temperature", get_temperature_report, name="get_temperature_report"),
    path('equipments/<str:equipment_id>/update/', update_equipment_status, name='update_equipment'),
    path("rooms/<int:room_id>/actions", perform_action, name="perform_action"),
    path("", api_root, name="api_root"),
]