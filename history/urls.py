from django.urls import path
from .views import get_realtime_data

urlpatterns = [
    path("air-quality/<str:room_name>/", get_realtime_data, name="get_realtime_data"),
]
