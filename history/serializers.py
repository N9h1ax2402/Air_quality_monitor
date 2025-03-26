from rest_framework import serializers
from .models import AirQualityHistory

class AirQualityHistorySerializer(serializers.Serializer):
    room_name = serializers.CharField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    light = serializers.FloatField()
    time = serializers.DateTimeField()

    def create(self, validated_data):
        return AirQualityHistory(**validated_data).save()
