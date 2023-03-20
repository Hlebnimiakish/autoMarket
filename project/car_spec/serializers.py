# pylint: skip-file

from rest_framework.serializers import ModelSerializer

from .models import (DealerSearchCarSpecificationModel, DealerSuitableCarModel,
                     DealerSuitableSellerModel)


class DealerSearchCarSpecificationsSerializer(ModelSerializer):
    class Meta:
        model = DealerSearchCarSpecificationModel
        fields = '__all__'
        read_only_fields = ['is_active', 'dealer']


class DealerSearchCarSpecificationEstFieldsSerializer(ModelSerializer):
    class Meta:
        model = DealerSearchCarSpecificationModel
        fields = ['transmission', 'body_type', 'engine_fuel_type',
                  'drive_unit', 'color', 'engine_volume',
                  'min_year_of_production', "safe_controls",
                  "parking_help", "climate_controls", "multimedia",
                  "additional_safety", "other_additions"]


class DealerSuitableCarModelsSerializer(ModelSerializer):
    class Meta:
        model = DealerSuitableCarModel
        fields = '__all__'


class DealerSuitableSellerSerializer(ModelSerializer):
    class Meta:
        model = DealerSuitableSellerModel
        fields = '__all__'
