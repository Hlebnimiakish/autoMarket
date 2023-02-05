from models import MarketAvailableCarModel
from rest_framework.serializers import ModelSerializer


class MarkerAvailableCarsModelSerializer(ModelSerializer):
    class Meta:
        model = MarketAvailableCarModel
        fields = '__all__'
