from django.urls import path
from .views import *

urlpatterns = [
    path('air-quality/<str:room_name>/', get_realtime_data, name='get_realtime_data'),
    path("main/weather", get_weather_info, name="get_weather_info"),
    path("main/room", get_room_list, name="get_room_list"),
    path("rooms/<int:room_id>/equipments", get_equipments, name="get_equipments"),
    path("rooms/<int:room_id>/parameters", get_air_parameters, name="get_air_parameters"),
    path("rooms/<int:room_id>/humidity", get_humidity_report, name="get_humidity_report"),
    path("rooms/<int:room_id>/temperature", get_temperature_report, name="get_temperature_report"),

    path("rooms/<int:room_id>/actions", perform_action, name="perform_action"),
]