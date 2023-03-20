# pylint: skip-file

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from root.common.permissions import (CurrentDealerHasNoSpec, IsDealer,
                                     IsOwnerOrAdmin, IsSeller, IsVerified)
from root.common.views import (BaseOwnModelReadView, BaseOwnModelRUDView,
                               BaseReadOnlyView, CustomRequest)
from user.models import AutoDealerModel

from .models import DealerSearchCarSpecificationModel, DealerSuitableCarModel
from .serializers import (DealerSearchCarSpecificationsSerializer,
                          DealerSuitableCarModelsSerializer)
from .spec_filter import SuitableCarFrontFilter, SuitableCarOwnFilter
from .tasks import task_find_suit_cars_for_dealer


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
        user = self.request.user
        spec = serializer.save(dealer=AutoDealerModel.objects.get(user=user))
        task_find_suit_cars_for_dealer.apply_async(spec, countdown=5)

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DealerSearchCarSpecificationRUDView(BaseOwnModelRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = DealerSearchCarSpecificationsSerializer
    model = DealerSearchCarSpecificationModel
    user_data = 'dealer'
    user_model = AutoDealerModel

    def put(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        serialized_new_obj = self.serializer(data=request.data,
                                             instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        spec = serialized_new_obj.save()
        task_find_suit_cars_for_dealer.apply_async(spec, countdown=5)
        return Response(serialized_new_obj.data)


class DealerSuitableCarFrontView(BaseReadOnlyView):
    permission_classes = [IsSeller & IsVerified]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel
    filterset_class = SuitableCarFrontFilter


class DealerSuitableCarOwnReadView(BaseOwnModelReadView):
    permission_classes = [IsDealer & IsVerified & IsOwnerOrAdmin]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel
    user_type = 'dealer'
    user_model = AutoDealerModel
    filterset_class = SuitableCarOwnFilter
