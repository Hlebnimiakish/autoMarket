from models import (CarBuyerHistoryModel, DealerSalesHistoryModel,
                    SellerSalesHistoryModel)
from rest_framework import generics
from rest_framework.mixins import ListModelMixin
from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import CustomRequest
from serializers import (CarBuyersHistorySerializer,
                         DealerSalesHistorySerializer,
                         SellerSalesHistorySerializer)


class SellerSalesHistoryView(ListModelMixin,
                             generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = SellerSalesHistoryModel.objects.all()
    serializer_class = SellerSalesHistorySerializer

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BuyerPurchaseHistoryView(ListModelMixin,
                               generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = CarBuyerHistoryModel.objects.all()
    serializer_class = CarBuyersHistorySerializer

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSalesHistoryView(ListModelMixin,
                             generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsSeller & IsVerified]
    queryset = DealerSalesHistoryModel.objects.all()
    serializer_class = DealerSalesHistorySerializer

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)
