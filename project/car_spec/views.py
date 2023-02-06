from typing import Type

from rest_framework import generics, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from root.common.models import BaseModel
from root.common.permissions import (CurrentDealerHasNoSpec, IsDealer,
                                     IsOwnerOrAdmin, IsSeller, IsVerified)
from root.common.views import BaseOwnModelRUDView, CustomRequest
from user.models import AutoDealerModel

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel
from .serializers import (DealerSearchCarSpecificationsSerializer,
                          DealerSuitableCarModelsSerializer)


class BaseBondedCarView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    filter_add_data: str

    def list(self, request: CustomRequest) -> Response:
        objs_set = self.model.objects.all()
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, id: int) -> Response:
        all_list_personal = self.model.objects.filter(**{self.filter_add_data: id})
        serialized_list_personal = self.serializer(all_list_personal, many=True)
        return Response(serialized_list_personal.data)


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


class DealerSuitableCarView(BaseBondedCarView):
    permission_classes = [IsSeller & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel
    filter_add_data = 'dealer'
