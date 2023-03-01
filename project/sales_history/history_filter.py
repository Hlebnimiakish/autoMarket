from django_filters.rest_framework import DateFilter, FilterSet, NumberFilter

from .models import (BaseSalesHistoryModel, CarBuyerHistoryModel,
                     DealerSalesHistoryModel, SellerSalesHistoryModel)


class BaseSalesHistoryFilter(FilterSet):
    after_date = DateFilter(field_name='date', lookup_expr='gte')
    before_date = DateFilter(field_name='date', lookup_expr='lte')
    min_selling_price = NumberFilter(field_name='selling_price', lookup_expr='gte')
    max_selling_price = NumberFilter(field_name='selling_price', lookup_expr='lte')
    min_sold_cars_quantity = NumberFilter(field_name='sold_cars_quantity', lookup_expr='gte')
    max_sold_cars_quantity = NumberFilter(field_name='sold_cars_quantity', lookup_expr='lte')
    min_deal_sum = NumberFilter(field_name='deal_sum', lookup_expr='gte')
    max_deal_sum = NumberFilter(field_name='deal_sum', lookup_expr='lte')

    class Meta:
        model = BaseSalesHistoryModel
        fields: list = []


class DealerSalesHistoryFilter(BaseSalesHistoryFilter):

    class Meta:
        model = DealerSalesHistoryModel
        fields = ['sold_car_model', 'car_buyer',
                  'selling_price', 'sold_cars_quantity',
                  'deal_sum']


class SellerSalesHistoryFilter(BaseSalesHistoryFilter):

    class Meta:
        model = SellerSalesHistoryModel
        fields = ['sold_car_model', 'car_buyer',
                  'selling_price', 'sold_cars_quantity',
                  'deal_sum']


class BuyerPurchaseHistoryFilter(FilterSet):
    min_bought_quantity = NumberFilter(field_name='bought_quantity', lookup_expr='gte')
    max_bought_quantity = NumberFilter(field_name='bought_quantity', lookup_expr='lte')
    min_car_price = NumberFilter(field_name='car_price', lookup_expr='gte')
    max_car_price = NumberFilter(field_name='car_price', lookup_expr='lte')
    min_deal_sum = NumberFilter(field_name='deal_sum', lookup_expr='gte')
    max_deal_sum = NumberFilter(field_name='deal_sum', lookup_expr='lte')
    after_date = DateFilter(field_name='date', lookup_expr='gte')
    before_date = DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = CarBuyerHistoryModel
        fields = ['bought_car_model', 'auto_dealer',
                  'bought_quantity', 'car_price',
                  'deal_sum']
