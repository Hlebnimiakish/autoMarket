from django_filters.rest_framework import FilterSet

from .models import DealerSuitableCarModel


class SuitableCarFrontFilter(FilterSet):

    class Meta:
        model = DealerSuitableCarModel
        fields = ['car_model', 'dealer']


class SuitableCarOwnFilter(FilterSet):
    class Meta:
        model = DealerSuitableCarModel
        fields = ['car_model']
