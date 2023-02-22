from car_park.views import BaseOwnBondedCarView
from rest_framework import generics
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from root.common.permissions import (CurrentDealerHasNoSpec, IsDealer,
                                     IsOwnerOrAdmin, IsSeller, IsVerified)
from root.common.views import (BaseOwnModelRUDView, BaseReadOnlyView,
                               CustomRequest)
from user.models import AutoDealerModel

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel
from .serializers import (DealerSearchCarSpecificationsSerializer,
                          DealerSuitableCarModelsSerializer)


class DealerSearchCarSpecificationView(ListModelMixin,
                                       generics.GenericAPIView):
    permission_classes = [IsSeller & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer
    queryset = DealerSearchCarSpecificationModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSearchCarSpecificationCreateView(CreateModelMixin,
                                             generics.GenericAPIView):
    permission_classes = [IsDealer & IsVerified & CurrentDealerHasNoSpec]
    serializer_class = DealerSearchCarSpecificationsSerializer

    def perform_create(self, serializer) -> None:
        self.request: CustomRequest
        user = self.request.user
        serializer.save(dealer=AutoDealerModel.objects.get(user=user))

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DealerSearchCarSpecificationRUDView(BaseOwnModelRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = DealerSearchCarSpecificationsSerializer
    model = DealerSearchCarSpecificationModel
    user_data = 'dealer'
    user_model = AutoDealerModel


class DealerSuitableCarFrontView(BaseReadOnlyView):
    permission_classes = [IsSeller & IsVerified]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel


class DealerSuitableCarOwnView(BaseOwnBondedCarView):
    permission_classes = [IsSeller & IsVerified & IsOwnerOrAdmin]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel
    user_type = 'dealer'
    user_model = AutoDealerModel
