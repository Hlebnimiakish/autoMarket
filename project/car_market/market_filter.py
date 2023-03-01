from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter

from .models import MarketAvailableCarModel


class CarFilter(FilterSet):
    max_engine_volume = NumberFilter(field_name="engine_volume", lookup_expr="lte")
    min_engine_volume = NumberFilter(field_name="engine_volume", lookup_expr="gte")
    color = CharFilter(field_name="color", lookup_expr="icontains")
    brand_name = CharFilter(field_name="brand_name", lookup_expr="icontains")
    car_model_name = CharFilter(field_name="car_model_name", lookup_expr="icontains")
    min_year_of_production = NumberFilter(field_name="year_of_production", lookup_expr="gte")
    max_year_of_production = NumberFilter(field_name="year_of_production", lookup_expr="lte")
    min_demand_level = NumberFilter(field_name="demand_level", lookup_expr="gte")
    max_demand_level = NumberFilter(field_name="demand_level", lookup_expr="lte")

    class Meta:
        model = MarketAvailableCarModel
        fields = ['engine_volume', 'drive_unit', 'engine_fuel_type',
                  'transmission', 'body_type', 'safe_controls',
                  'parking_help', 'climate_controls', 'multimedia',
                  'additional_safety', 'other_additions']
