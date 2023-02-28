from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from root.common.views import BaseReadOnlyView

from .market_filter import CarFilter
from .models import MarketAvailableCarModel
from .serializers import MarkerAvailableCarsModelSerializer


class MarketAvailableCarModelView(BaseReadOnlyView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filterset_class = CarFilter
    search_fields = ['brand_name', 'car_model_name']
    ordering_fields = ['engine_volume', 'year_of_production',
                       'demand_level']
