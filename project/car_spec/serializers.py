from rest_framework.serializers import ModelSerializer

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel


class DealerSearchCarSpecificationsSerializer(ModelSerializer):
    class Meta:
        model = DealerSearchCarSpecificationModel
        fields = '__all__'
        read_only_fields = ['is_active', 'dealer']


class DealerSuitableCarModelsSerializer(ModelSerializer):
    class Meta:
        model = DealerSuitableCarModel
        fields = '__all__'
