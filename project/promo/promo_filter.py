from django_filters.rest_framework import (CharFilter, DateTimeFilter,
                                           FilterSet, NumberFilter)

from .models import BasePromoModel, DealerPromoModel, SellerPromoModel


class BasePromoFilter(FilterSet):
    promo_name = CharFilter(field_name="promo_name", lookup_expr="icontains")
    promo_description = CharFilter(field_name="promo_description", lookup_expr="icontains")
    start_after_date = DateTimeFilter(field_name="start_date", lookup_expr="gte")
    start_before_date = DateTimeFilter(field_name="start_date", lookup_expr="lte")
    end_date = DateTimeFilter(field_name="end_date", lookup_expr="gte")
    discount_size = NumberFilter(field_name="discount_size", lookup_expr="gte")

    class Meta:
        model = BasePromoModel
        fields: list = []


class PromoFilterDealer(BasePromoFilter):
    class Meta:
        model = DealerPromoModel
        fields = ['creator', 'promo_aims', 'promo_cars']


class PromoFilterSeller(BasePromoFilter):
    class Meta:
        model = SellerPromoModel
        fields = ['creator', 'promo_aims', 'promo_cars']
