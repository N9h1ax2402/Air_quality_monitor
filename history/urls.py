from django.urls import path
from .views import get_history_data

urlpatterns = [
    path("abnormal-reports/<str:room_name>/", get_history_data, name="get_history_data"),
]
