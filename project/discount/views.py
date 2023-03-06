from rest_framework import filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified, SellerHasNoDiscountSet)
from root.common.views import (BaseOwnModelReadView, BaseOwnModelRUDView,
                               BaseReadOnlyView, CustomRequest)
from user.models import AutoDealerModel, AutoSellerModel

from .models import CurrentDiscountLevelPerDealerModel
from .models import RegularCustomerDiscountLevelsModel as DiscountLevels
from .serializers import CurrentDiscountLevelPerDealerSerializer
from .serializers import \
    RegularCustomerDiscountLevelsSerializer as DiscountLevelsSerializer


class SellerDiscountLevelsView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = DiscountLevelsSerializer
    model = DiscountLevels
    filter_backends = (filters.SearchFilter,)
    search_fields = ['seller__name']


class MyCurrentDiscountLevelsView(BaseOwnModelReadView):
    permission_classes = [IsDealer & IsVerified]
    model = CurrentDiscountLevelPerDealerModel
    serializer = CurrentDiscountLevelPerDealerSerializer
    user_type = 'dealer'
    user_model = AutoDealerModel


class AllCurrentDiscountLevelsView(BaseOwnModelReadView):
    permission_classes = [IsSeller & IsVerified]
    model = CurrentDiscountLevelPerDealerModel
    serializer = CurrentDiscountLevelPerDealerSerializer
    user_type = 'seller'
    user_model = AutoSellerModel


class SellerDiscountsRUDView(BaseOwnModelRUDView):
    permission_classes = [IsSeller & IsOwnerOrAdmin & IsVerified]
    serializer = DiscountLevelsSerializer
    model = DiscountLevels
    user_data = 'seller'
    user_model = AutoSellerModel


class SellerDiscountsCreateView(APIView):
    permission_classes = [IsSeller & SellerHasNoDiscountSet & IsVerified]

    def post(self, request: CustomRequest) -> Response:
        user_data = {'seller': AutoSellerModel.objects.get(user=request.user)}
        serialized_obj = DiscountLevelsSerializer(data=request.data)
        serialized_obj.is_valid(raise_exception=True)
        serialized_obj.save(**user_data)
        return Response(serialized_obj.data, status=status.HTTP_201_CREATED)
