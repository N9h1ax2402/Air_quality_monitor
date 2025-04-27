from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import AirQualityConsumer  

# api/routing.py
websocket_urlpatterns = [
    re_path(r'ws/air-quality/(?P<room_id>\w+)/$', AirQualityConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": URLRouter(websocket_urlpatterns),
})
