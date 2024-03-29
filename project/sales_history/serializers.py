from rest_framework.serializers import ModelSerializer

from .models import (CarBuyerHistoryModel, DealerSalesHistoryModel,
                     SellerSalesHistoryModel)


class DealerSalesHistorySerializer(ModelSerializer):
    class Meta:
        model = DealerSalesHistoryModel
        fields = '__all__'


class SellerSalesHistorySerializer(ModelSerializer):
    class Meta:
        model = SellerSalesHistoryModel
        fields = '__all__'


class CarBuyersHistorySerializer(ModelSerializer):
    class Meta:
        model = CarBuyerHistoryModel
        fields = '__all__'
