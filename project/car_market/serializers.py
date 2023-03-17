# pylint: skip-file

from rest_framework.serializers import ModelSerializer

from .models import MarketAvailableCarModel


class MarkerAvailableCarsModelSerializer(ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = '__all__'


class MarketAvailableCarsModelSomeFielsSerializer(ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = ['id', 'transmission', 'body_type', 'engine_fuel_type',
                  'drive_unit', 'color', 'engine_volume',
                  'year_of_production', "safe_controls",
                  "parking_help", "climate_controls", "multimedia",
                  "additional_safety", "other_additions"]
