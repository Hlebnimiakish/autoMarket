from rest_framework.serializers import ModelSerializer

from .models import OfferModel


class OffersSerializer(ModelSerializer):
    class Meta:
        model = OfferModel
        read_only_fields = ['is_active', 'creator']
        fields = '__all__'
