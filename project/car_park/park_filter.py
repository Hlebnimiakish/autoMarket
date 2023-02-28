from django_filters.rest_framework import FilterSet, NumberFilter

from .models import (BaseCurrentCarParkModel, DealerCarParkModel,
                     SellerCarParkModel)


class BaseParkFilter(FilterSet):
    min_available_number = NumberFilter(field_name="available_number", lookup_expr="gte")
    max_car_price = NumberFilter(field_name="car_price", lookup_expr="lte")
    min_car_price = NumberFilter(field_name="car_price", lookup_expr="gte")

    class Meta:
        model = BaseCurrentCarParkModel
        fields: list = []


class DealerParkFilter(BaseParkFilter):

    class Meta:
        model = DealerCarParkModel
        fields = ['car_model', 'dealer']


class SellerParkFilter(BaseParkFilter):

    class Meta:
        model = SellerCarParkModel
        fields = ['car_model', 'seller']
