from django.urls import path
from .views import *

urlpatterns = [
    path("", homepage, name="homepage"),
    path("debug/routes/", list_routes, name="debug_routes"),
    path('air-quality/<str:room_name>/', get_realtime_data, name='get_realtime_data'),
]