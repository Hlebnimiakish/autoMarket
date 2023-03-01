from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsSeller, IsVerified)
from root.common.views import BaseOwnModelReadView
from user.models import AutoDealerModel, AutoSellerModel, CarBuyerModel

from .history_filter import (BuyerPurchaseHistoryFilter,
                             DealerSalesHistoryFilter,
                             SellerSalesHistoryFilter)
from .models import (CarBuyerHistoryModel, DealerSalesHistoryModel,
                     SellerSalesHistoryModel)
from .serializers import (CarBuyersHistorySerializer,
                          DealerSalesHistorySerializer,
                          SellerSalesHistorySerializer)


class SellerSalesHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsSeller & IsOwnerOrAdmin]
    model = SellerSalesHistoryModel
    serializer = SellerSalesHistorySerializer
    user_model = AutoSellerModel
    user_type = 'seller'
    filterset_class = SellerSalesHistoryFilter
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    search_fields = ['sold_car_model__car_model__car_model_name']
    ordering_fields = ['deal_sum', 'date',
                       'sold_cars_quantity', 'selling_price']


class DealerSalesHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsDealer & IsOwnerOrAdmin]
    model = DealerSalesHistoryModel
    serializer = DealerSalesHistorySerializer
    user_model = AutoDealerModel
    user_type = 'dealer'
    filterset_class = DealerSalesHistoryFilter
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    search_fields = ['sold_car_model__car_model__car_model_name']
    ordering_fields = ['deal_sum', 'date',
                       'sold_cars_quantity', 'selling_price']


class BuyerPurchaseHistoryOwnView(BaseOwnModelReadView):
    permission_classes = [IsVerified & IsBuyer & IsOwnerOrAdmin]
    model = CarBuyerHistoryModel
    serializer = CarBuyersHistorySerializer
    user_model = CarBuyerModel
    user_type = 'buyer'
    filterset_class = BuyerPurchaseHistoryFilter
    filter_backends = (DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    search_fields = ['bought_car_model__car_model__car_model_name']
    ordering_fields = ['deal_sum', 'date',
                       'bought_quantity', 'car_price']
