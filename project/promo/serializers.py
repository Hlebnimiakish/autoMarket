from rest_framework.serializers import ModelSerializer

from .models import DealerPromoModel, SellerPromoModel


class DealersPromoSerializer(ModelSerializer):
    class Meta:
        model = DealerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'


class SellersPromoSerializer(ModelSerializer):
    class Meta:
        model = SellerPromoModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
