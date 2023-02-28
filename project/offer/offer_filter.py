from django_filters.rest_framework import FilterSet, NumberFilter

from .models import OfferModel


class OfferFilter(FilterSet):
    min_max_price = NumberFilter(field_name="max_price", lookup_expr="gte")
    max_max_price = NumberFilter(field_name="max_price", lookup_expr="lte")

    class Meta:
        model = OfferModel
        fields = ['car_model', 'creator']
