from django_filters.rest_framework import FilterSet

from .models import AutoDealerModel


class AutoDealerFilter(FilterSet):
    class Meta:
        model = AutoDealerModel
        fields = ['home_country']
