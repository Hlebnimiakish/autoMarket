from rest_framework.serializers import ModelSerializer

from .models import MarketAvailableCarModel


class MarkerAvailableCarsModelSerializer(ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = '__all__'
