# mypy: disable-error-code=override

from typing import Type

from django.contrib.auth import login, logout
from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from user_app.models import (AutoDealerModel, AutoSellerModel, BaseModel,
                             CarBuyerHistoryModel, CarBuyerModel,
                             CustomUserModel, DealerCarParkModel,
                             DealerPromoModel, DealerSalesHistoryModel,
                             DealerSearchCarSpecificationModel,
                             DealerSuitableCarModel, MarketAvailableCarModel,
                             OfferModel, SellerCarParkModel, SellerPromoModel,
                             SellerSalesHistoryModel)

from .api_permissions import (IsBuyer, IsDealer, IsOwnerOrAdmin, IsSeller,
                              IsThisUser, IsVerified)
from .serializers import (AutoDealerFrontSerializer, AutoDealerSerializer,
                          AutoSellerFrontSerializer, AutoSellersSerializer,
                          CarBuyersFrontSerializer, CarBuyersSerializer,
                          CustomUserSerializer, DealerCarParkSerializer,
                          DealerSearchCarSpecificationsSerializer,
                          DealersPromoSerializer,
                          DealerSuitableCarModelsSerializer,
                          MarkerAvailableCarsModelSerializer, OffersSerializer,
                          SellersCarParkSerializer, SellersPromoSerializer)


class CustomRequest(Request):
    user: CustomUserModel


class BaseReadOnlyView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]

    def list(self, request: CustomRequest) -> Response:
        objs_set = self.model.objects.all()
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, id: int) -> Response:
        obj = get_object_or_404(self.model.objects.all(), id=id)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)


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


class BaseOwnModelRUDView(APIView):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    user_data: str
    user_model: Type[BaseModel | Model]

    def profile_getter(self, request: CustomRequest) -> BaseModel | Model:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def get(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def post(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        context = {self.user_data: self.profile_getter(request)}
        serialized_new_obj = self.serializer(data=request.data,
                                             instance=obj,
                                             context=context)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def delete(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)


class BaseOwnProfileRUDView(BaseOwnModelRUDView):
    user_model: CustomUserModel = CustomUserModel  # type: ignore[assignment]
    user_data = 'user'

    def profile_getter(self, request: CustomRequest) -> CustomUserModel:
        user = self.user_model.objects.get(id=request.user.id)
        return user


class BaseCRUDView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    user_data: str
    user_model: Type[BaseModel | Model]

    def profile_getter(self, request: CustomRequest) -> BaseModel | Model:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def retrieve(self, request: CustomRequest, id: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=id)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request: CustomRequest, id: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=id)
        context = {self.user_data: self.profile_getter(request)}
        serialized_new_obj = self.serializer(data=request.data,
                                             instance=obj,
                                             context=context)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request: CustomRequest, id: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=id)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def create(self, request: CustomRequest) -> Response:
        context = {self.user_data: self.profile_getter(request)}
        serialized_obj = self.serializer(data=request.data, context=context)
        serialized_obj.is_valid(raise_exception=True)
        serialized_obj.save()
        return Response(serialized_obj.data)

    def list(self, request: CustomRequest) -> Response:
        objs = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        serialized_objs = self.serializer(objs, many=True)
        return Response(serialized_objs.data)


class BaseProfileCreationView(CreateModelMixin,
                              generics.GenericAPIView):
    def perform_create(self, serializer) -> None:
        user = self.request.user
        serializer.save(user_id=user.pk)

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: CustomRequest) -> Response:
        user = CustomUserModel.objects.get(email=request.data['email'],
                                           password=request.data['password'])
        login(request, user)
        return Response(status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    def get(self, request: CustomRequest) -> Response:
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CustomUserCreationView(CreateModelMixin,
                             generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request: CustomRequest, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SelfUserProfileRUDView(BaseOwnModelRUDView):
    permission_classes = [IsThisUser]
    serializer = CustomUserSerializer
    model: CustomUserModel = CustomUserModel  # type: ignore[assignment]
    user_data = 'id'

    def profile_getter(self, request: CustomRequest) -> int:
        id = request.user.id
        return id


class AutoDealerReadOnlyView(BaseReadOnlyView):
    serializer = AutoDealerFrontSerializer
    model = AutoDealerModel


class AutoSellerReadOnlyView(BaseReadOnlyView):
    permission_classes = [IsSeller & IsVerified | IsDealer & IsVerified]
    serializer = AutoSellerFrontSerializer
    model = AutoSellerModel


class CarBuyerReadOnlyView(BaseReadOnlyView):
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


class AutoDealerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoDealerSerializer
    model = AutoDealerModel


class CarBuyerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = CarBuyersSerializer
    model = CarBuyerModel


class AutoSellerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoSellersSerializer
    model = AutoSellerModel


class MarketAvailableCarModelView(BaseReadOnlyView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel


class DealerSearchCarSpecificationView(ListModelMixin,
                                       generics.GenericAPIView):
    permission_classes = [IsSeller & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer
    queryset = DealerSearchCarSpecificationModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSearchCarSpecificationCreateView(CreateModelMixin,
                                             generics.GenericAPIView):
    permission_classes = [IsDealer & IsVerified]
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


class DealerAutoParkView(BaseBondedCarView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel
    filter_add_data = 'dealer'


class SellerAutoParkView(BaseBondedCarView):
    permission_classes = [IsDealer & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel
    filter_add_data = 'seller'


class SellerSalesHistoryView(ListModelMixin,
                             generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = SellerSalesHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BuyerPurchaseHistoryView(ListModelMixin,
                               generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = CarBuyerHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSalesHistoryView(ListModelMixin,
                             generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsSeller & IsVerified]
    queryset = DealerSalesHistoryModel.objects.all()

    def get(self, request: CustomRequest, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerPromoReadOnlyView(BaseReadOnlyView):
    serializer = DealersPromoSerializer
    model = DealerPromoModel


class SellerPromoReadOnlyView(BaseReadOnlyView):
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


class OfferForDealerView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = OffersSerializer
    model = OfferModel


class OfferCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel
    user_data = 'creator'
    user_model = CarBuyerModel
