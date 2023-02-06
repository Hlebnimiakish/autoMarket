from models import DealerPromoModel, SellerPromoModel
from rest_framework.serializers import ModelSerializer


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
