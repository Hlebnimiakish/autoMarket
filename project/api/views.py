from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import login, logout
from rest_framework.views import APIView
import typing
from django.db import models
from rest_framework import serializers

from serializers import AutoDealerSerializer, AutoSellersSerializer, CustomUserSerializer, OffersSerializer, \
    AutoDealerFrontSerializer, AutoSellerFrontSerializer, CarBuyersFrontSerializer, CarBuyersSerializer, \
    MarkerAvailableCarsModelSerializer, DealerSearchCarSpecificationsSerializer, DealerSuitableCarModelsSerializer, \
    DealerCarParkSerializer, SellersCarParkSerializer, DealersPromoSerializer, SellersPromoSerializer
from user_app.models import CustomUserModel, AutoDealerModel, DealerSearchCarSpecificationModel, MarketAvailableCarModel, \
    DealerSuitableCarModel, DealerCarParkModel, AutoSellerModel, SellerCarParkModel, DealerSalesHistoryModel, \
    SellerSalesHistoryModel, CarBuyerModel, CarBuyerHistoryModel, OfferModel, DealerPromoModel, SellerPromoModel,\
    BaseActiveStatusModel
from api_permissions import IsOwnerOrAdmin, IsDealer, IsSeller, IsBuyer, IsThisUser, IsVerified

# M = typing.TypeVar('M', bound=models.Model | BaseActiveStatusModel, covariant=True)
# S = typing.TypeVar('S', bound=serializers.ModelSerializer, covariant=True)
# UM = typing.TypeVar('UM', bound=AutoSellerModel | AutoDealerModel | CarBuyerModel | CustomUserModel, covariant=True)


class CustomRequest(Request):
    user: CustomUserModel


class BaseForOtherUsersView(viewsets.ViewSet):
    model: typing.Type[BaseActiveStatusModel]
    serializer: typing.Type[serializers.ModelSerializer]

    def list(self, request: CustomRequest) -> Response:
        objs_set = self.model.objects.filter(is_active=True)
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, id: int | None = None) -> Response:
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, id=id)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)


class BaseBondedCarsView(BaseForOtherUsersView):
    filter_add_data: str

    def retrieve(self, request: CustomRequest, id: int | None = None) -> Response:
        all_list_personal = self.model.objects.filter(is_active=True, **{self.filter_add_data: id})
        serialized_list_personal = self.serializer(all_list_personal, many=True)
        return Response(serialized_list_personal.data)


class BaseRUDView(viewsets.ViewSet):
    model: typing.Type[BaseActiveStatusModel | typing.Any]
    serializer: typing.Type[serializers.ModelSerializer]
    user_data: str
    user_model: typing.Type[AutoSellerModel | AutoDealerModel | CarBuyerModel | typing.Any]

    def profile_getter(self, request: CustomRequest) -> typing.Union[AutoDealerModel, AutoSellerModel,
                                                                     CarBuyerModel, AnonymousUser, typing.Any]:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def retrieve(self, request: CustomRequest, id: int | None = None) -> Response:
        objs_set = self.model.objects.filter(is_active=True,
                                             **{self.user_data: self.profile_getter(request)})
        if id:
            obj = get_object_or_404(objs_set, id=id)
        else:
            obj = get_object_or_404(objs_set)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request: CustomRequest, id: int | None = None) -> Response:
        objs_set = self.model.objects.filter(is_active=True)
        if id:
            obj = get_object_or_404(objs_set, id=id)
        else:
            obj = get_object_or_404(objs_set)
        context = {self.user_data: self.profile_getter(request)}
        serialized_new_obj = self.serializer(data=request.data, instance=obj,
                                             context=context)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request: CustomRequest, id: int | None = None) -> Response:
        objs_set = self.model.objects.filter(is_active=True,
                                             **{self.user_data: self.profile_getter(request)})
        if id:
            obj = get_object_or_404(objs_set, id=id)
        else:
            obj = get_object_or_404(objs_set)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)


class BaseProfileRUDView(BaseRUDView):
    def profile_getter(self, request: CustomRequest) -> typing.Union[AutoSellerModel, AutoDealerModel,
                                                                     CarBuyerModel, CustomUserModel]:
        user = self.user_model.objects.get(id=request.user.id)
        return user


class BaseCRUDView(BaseRUDView):
    def create(self, request: CustomRequest) -> Response:
        context = {self.user_data: self.profile_getter(request)}
        serialized_obj = self.serializer(data=request.data, context=context)
        serialized_obj.is_valid(raise_exception=True)
        serialized_obj.save()
        return Response(serialized_obj.data)

    def list(self, request: CustomRequest) -> Response:
        objs = self.model.objects.filter(is_active=True,
                                         **{self.user_data: self.profile_getter(request)})
        serialized_objs = self.serializer(objs, many=True)
        return Response(serialized_objs.data)


class BaseProfileCreationView(CreateModelMixin, generics.GenericAPIView):
    def perform_create(self, serializer) -> None:
        user = self.request.user
        serializer.save(user_id=user.pk)

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: CustomRequest) -> Response:
        user = CustomUserModel.objects.get(email=request.data['email'], password=request.data['password'])
        login(request, user)
        return Response(status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    def get(self, request: CustomRequest) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CustomUserCreationView(CreateModelMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserProfileRUDView(BaseRUDView):
    permission_classes = [IsThisUser]
    serializer = CustomUserSerializer
    model = CustomUserModel
    user_data = 'id'

    def profile_getter(self, request: CustomRequest) -> typing.Union[int, str]:
        id = request.user.id
        return id


class AutoDealersForOtherUsersView(BaseForOtherUsersView):
    serializer = AutoDealerFrontSerializer
    model = AutoDealerModel


class AutoSellersForOtherUsersView(BaseForOtherUsersView):
    permission_classes = [IsSeller & IsVerified | IsDealer & IsVerified]
    serializer = AutoSellerFrontSerializer
    model = AutoSellerModel


class CarBuyersForOtherUsersView(BaseForOtherUsersView):
    permission_classes = [IsDealer & IsVerified]
    serializer = CarBuyersFrontSerializer
    model = CarBuyerModel


class AutoDealerCreateView(BaseProfileCreationView):
    permission_classes = [IsDealer & IsVerified]
    serializer_class = AutoDealerSerializer


class CarBuyerCreateView(BaseProfileCreationView):
    permission_classes = [IsBuyer & IsVerified]
    serializer_class = CarBuyersSerializer


class AutoSellerCreateView(BaseProfileCreationView):
    permission_classes = [IsSeller & IsVerified]
    serializer_class = AutoSellersSerializer


class AutoDealerRUDView(BaseProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoDealerSerializer
    model = AutoDealerModel
    user_model = CustomUserModel
    user_data = 'user'


class CarBuyerRUDView(BaseProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = CarBuyersSerializer
    model = CarBuyerModel
    user_model = CustomUserModel
    user_data = 'user'


class AutoSellerRUDView(BaseProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoSellersSerializer
    model = AutoSellerModel
    user_model = CustomUserModel
    user_data = 'user'


class MarketAvailableCarModelsView(BaseForOtherUsersView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel


class DealerSearchCarSpecificationsView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsSeller & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer
    queryset = DealerSearchCarSpecificationModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSearchCarsSpecificationsCreateView(CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsDealer & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer

    def perform_create(self, serializer) -> None:
        self.request: CustomRequest
        user = self.request.user
        serializer.save(dealer=AutoDealerModel.objects.get(user=user))

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DealerSearchCarsSpecificationRUDView(BaseRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = DealerSearchCarSpecificationsSerializer
    model = DealerSearchCarSpecificationModel
    user_data = 'dealer'
    user_model = AutoDealerModel


class DealerSuitableCarsView(BaseBondedCarsView):
    permission_classes = [IsSeller & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel
    filter_add_data = 'dealer'


class DealerAutoParkView(BaseBondedCarsView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    filter_add_data = 'dealer'


class SellerAutoParkView(BaseBondedCarsView):
    permission_classes = [IsDealer & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    filter_add_data = 'seller'


class SellerSellsHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = SellerSalesHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BuyerPurchaseHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = CarBuyerHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSellsHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsSeller & IsVerified]
    queryset = DealerSalesHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerPromoForOtherUsersView(BaseForOtherUsersView):
    serializer = DealersPromoSerializer
    model = DealerPromoModel


class SellerPromoForOtherUsersView(BaseForOtherUsersView):
    serializer = SellersPromoSerializer
    model = SellerPromoModel


class DealerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsDealer & IsOwnerOrAdmin & IsVerified]
    serializer = DealersPromoSerializer
    model = DealerPromoModel
    user_data = 'creator'
    user_model = AutoDealerModel


class SellerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsSeller & IsOwnerOrAdmin & IsVerified]
    serializer = SellersPromoSerializer
    model = SellerPromoModel
    user_data = 'creator'
    user_model = AutoSellerModel


class OffersForDealersView(BaseForOtherUsersView):
    permission_classes = [IsDealer & IsVerified]
    serializer = OffersSerializer
    model = OfferModel


class OffersCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    user_data = 'creator'
    user_model = CarBuyerModel
