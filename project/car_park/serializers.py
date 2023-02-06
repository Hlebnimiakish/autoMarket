from models import DealerCarParkModel, SellerCarParkModel
from rest_framework.serializers import ModelSerializer


class DealerCarParkSerializer(ModelSerializer):
    class Meta:
        model = DealerCarParkModel
        fields = '__all__'


class SellersCarParkSerializer(ModelSerializer):
    class Meta:
        model = SellerCarParkModel
        fields = '__all__'
