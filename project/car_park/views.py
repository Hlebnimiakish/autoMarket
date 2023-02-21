from typing import Type

from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from root.common.models import BaseModel
from root.common.permissions import (IsDealer, IsOwnerOrAdmin, IsSeller,
                                     IsVerified)
from root.common.views import BaseReadOnlyView, CustomRequest
from user.models import AutoDealerModel, AutoSellerModel

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


class BaseOwnBondedCarView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    user_type: str
    user_model: Type[BaseModel | Model]

    def profile_getter(self, request: CustomRequest) -> BaseModel | Model:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def list(self, request: CustomRequest) -> Response:
        profile = self.profile_getter(request)
        objs_set = self.model.objects.filter(**{self.user_type: profile})
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, pk: int) -> Response:
        profile = self.profile_getter(request)
        objs_set = self.model.objects.filter(**{self.user_type: profile})
        obj = get_object_or_404(objs_set, id=pk)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)


class DealerAutoParkFrontView(BaseReadOnlyView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel


class SellerAutoParkFrontView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel


class DealerOwnAutoParkView(BaseOwnBondedCarView):
    permission_classes = [IsDealer & IsVerified & IsOwnerOrAdmin]
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    user_type = 'dealer'
    user_model = AutoDealerModel


class SellerOwnAutoParkView(BaseOwnBondedCarView):
    permission_classes = [IsSeller & IsVerified & IsOwnerOrAdmin]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    user_type = 'seller'
    user_model = AutoSellerModel
