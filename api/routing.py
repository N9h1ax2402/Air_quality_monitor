from django.urls import re_path
from .consumers import AirQualityConsumer, WarningConsumer

websocket_urlpatterns = [
    # re_path(r'ws/air-quality/(?P<room_name>\w+)/$', AirQualityConsumer.as_asgi()),
    re_path(r'ws/warning', WarningConsumer.as_asgi()),
]
