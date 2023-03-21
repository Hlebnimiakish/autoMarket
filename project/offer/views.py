# pylint: skip-file

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.response import Response
from root.common.permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin,
                                     IsVerified)
from root.common.views import BaseCRUDView, BaseReadOnlyView, CustomRequest
from user.models import CarBuyerModel

from .models import OfferModel
from .offer_filter import OfferFilter
from .serializers import OffersSerializer
from .tasks import task_make_deal_from_offer


class OfferForDealerView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    filterset_class = OfferFilter
    filter_backends = (filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ['max_price']


class OfferCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    user_data = 'creator'
    user_model = CarBuyerModel

    def create(self, request: CustomRequest) -> Response:
        user_data = {self.user_data: self.profile_getter(request)}
        serialized_obj = self.serializer(data=request.data, context=user_data)
        serialized_obj.is_valid(raise_exception=True)
        new_offer = serialized_obj.save(**user_data)
        task_make_deal_from_offer.apply_async(new_offer, countdown=5)
        return Response(serialized_obj.data, status=status.HTTP_201_CREATED)

    def update(self, request: CustomRequest, pk: int) -> Response:
        user_data = {self.user_data: self.profile_getter(request)}
        objs_set = self.model.objects.filter(**user_data)
        obj = get_object_or_404(objs_set, id=pk)
        serialized_new_obj = self.serializer(data=request.data,
                                             context=user_data,
                                             instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        updated_offer = serialized_new_obj.save()
        task_make_deal_from_offer.apply_async(updated_offer, countdown=5)
        return Response(serialized_new_obj.data)
