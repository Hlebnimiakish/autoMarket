from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import login, logout
from rest_framework.views import APIView

from .serializers import *
from app.models import CustomUserModel, AutoDealerModel, DealerSearchCarSpecificationModel, MarketAvailableCarModel, \
    DealerSuitableCarModel, DealerCarParkModel, AutoSellerModel, SellerCarParkModel, DealerSalesHistoryModel, \
    SellerSalesHistoryModel, CarBuyerModel, CarBuyerHistoryModel, OfferModel, DealerPromoModel, SellerPromoModel
from .api_permissions import *


class BaseAllView(viewsets.ViewSet):
    model = CustomUserModel
    serializer = CustomUserSerializer

    def list(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request, id=None):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, id=id)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)


class BaseRUDView(viewsets.ViewSet):
    serializer = CustomUserSerializer
    model = CustomUserModel

    def retrieve(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, user=request.user)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, user=request.user)
        serialized_new_obj = self.serializer(data=request.data, instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, user=request.user)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)


class BaseCRUDView(viewsets.ViewSet):
    serializer = CustomUserSerializer
    model = CustomUserModel

    def profile_getter(self, request):
        user_profile = AutoDealerModel.objects.get(user=request.user)
        return user_profile

    def create(self, request):
        serialized_obj = self.serializer(data=request.data, creator=self.profile_getter(request))
        serialized_obj.is_valid(raise_exception=True)
        serialized_obj.save()
        return Response(serialized_obj.data)

    def list(self, request):
        objs = self.model.objects.filter(creator=self.profile_getter(request), is_active=True)
        serialized_objs = self.serializer(objs, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request, id=None):
        objs_set = self.model.objects.filter(creator=self.profile_getter(request), is_active=True)
        obj = get_object_or_404(objs_set, id=id)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request, id=None):
        objs_set = self.model.objects.filter(is_active=True, creator=self.profile_getter(request))
        obj = get_object_or_404(objs_set, id=id)
        serialized_new_obj = self.serializer(data=request.data, creator=self.profile_getter(request), instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request, id=None):
        objs_set = self.model.objects.filter(is_active=True, creator=self.profile_getter(request))
        obj = get_object_or_404(objs_set, id=id)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)


class BaseBondedCarsView(viewsets.ViewSet):
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel

    def list(self, request):
        all_list = self.model.objects.filter(is_active=True)
        serialized_list = self.serializer(all_list, many=True)
        return Response(serialized_list.data)

    def retrieve(self, request, id=None):
        all_list_personal = self.model.objects.filter(dealer=id, is_active=True)
        serialized_list_personal = self.serializer(all_list_personal, many=True)
        return Response(serialized_list_personal.data)


class BaseProfileCreationView(CreateModelMixin, generics.GenericAPIView):
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user_id=user.id)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

