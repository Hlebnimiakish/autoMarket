from models import OfferModel
from rest_framework.serializers import ModelSerializer


class OffersSerializer(ModelSerializer):
    class Meta:
        model = OfferModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
