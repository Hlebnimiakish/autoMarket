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


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = CustomUserModel.objects.get(email=request.data['email'], password=request.data['password'])
        login(request, user)
        return Response(status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class AmeUserCreationView(CreateModelMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AmeUserRUDView(viewsets.ViewSet):
    permission_classes = [IsThisUser]

    def retrieve(self, request):
        users_set = CustomUserModel.objects.filter(is_active=True)
        user_data = get_object_or_404(users_set, id=request.user.id)
        serialized_user = CustomUserSerializer(user_data)
        return Response(serialized_user.data)

    def update(self, request):
        users_set = CustomUserModel.objects.filter(is_active=True)
        user_data = get_object_or_404(users_set, id=request.user.id)
        serialized_new_user_data = CustomUserSerializer(data=request.data, instance=user_data)
        if serialized_new_user_data.is_valid():
            serialized_new_user_data.save()
            return Response(serialized_new_user_data.data)

    def destroy(self, request):
        users_set = CustomUserModel.objects.filter(is_active=True)
        user_data = get_object_or_404(users_set, id=request.user.id)
        user_data.is_active = False
        user_data.save()
        return Response(status=status.HTTP_200_OK)


class AutoDealersAllView(BaseAllView):
    serializer = AutoDealerFrontSerializer
    model = AutoDealerModel


class AutoSellersAllView(BaseAllView):
    permission_classes = [IsSeller & IsVerified | IsDealer & IsVerified]
    serializer = AutoSellerFrontSerializer
    model = AutoSellerModel


class CarBuyersAllView(BaseAllView):
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


class AutoDealerRUDView(BaseRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoDealerSerializer
    model = AutoDealerModel


class CarBuyerRUDView(BaseRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = CarBuyersSerializer
    model = CarBuyerModel


class AutoSellerRUDView(BaseRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoSellersSerializer
    model = AutoSellerModel


class MarketAvailableCarsModelView(BaseAllView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel


class DealerSearchCarSpecificationsView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsSeller & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer
    queryset = DealerSearchCarSpecificationModel.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSearchCarsSpecificationsCreateView(CreateModelMixin, generics.GenericAPIView):
    permission_classes = [IsDealer & IsVerified]
    serializer_class = DealerSearchCarSpecificationsSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(dealer=AutoDealerModel.objects.get(user=user))

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DealerSearchCarsSpecificationRUDView(BaseRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = DealerSearchCarSpecificationsSerializer
    model = DealerSearchCarSpecificationModel

    def retrieve(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, dealer=AutoDealerModel.objects.get(user=request.user))
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, dealer=AutoDealerModel.objects.get(user=request.user))
        serialized_new_obj = self.serializer(data=request.data, instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request):
        objs_set = self.model.objects.filter(is_active=True)
        obj = get_object_or_404(objs_set, dealer=AutoDealerModel.objects.get(user=request.user))
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)


class DealerSuitableCarsView(BaseBondedCarsView):
    permission_classes = [IsSeller & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = DealerSuitableCarModelsSerializer
    model = DealerSuitableCarModel


class DealerAutoParkView(BaseBondedCarsView):
    serializer = DealerCarParkSerializer
    model = DealerCarParkModel


class SellerAutoParkView(BaseBondedCarsView):
    permission_classes = [IsDealer & IsVerified | IsOwnerOrAdmin & IsVerified]
    serializer = SellersCarParkSerializer
    model = SellerCarParkModel

    def retrieve(self, request, id=None):
        car_park = SellerCarParkModel.objects.filter(seller=id, is_active=True)
        serialized_park = SellersCarParkSerializer(car_park, many=True)
        return Response(serialized_park.data)


class SellerSellsHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = SellerSalesHistoryModel.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BuyerPurchaseHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsDealer & IsVerified]
    queryset = CarBuyerHistoryModel.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerSellsHistoryView(ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdmin & IsVerified | IsSeller & IsVerified]
    queryset = DealerSalesHistoryModel.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DealerPromoAllView(BaseAllView):
    serializer = DealersPromoSerializer
    model = DealerPromoModel


class SellerPromoAllView(BaseAllView):
    serializer = SellersPromoSerializer
    model = SellerPromoModel


class DealerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsDealer & IsOwnerOrAdmin & IsVerified]
    serializer = DealersPromoSerializer
    model = DealerPromoModel

    def profile_getter(self, request):
        user_profile = AutoDealerModel.objects.get(user=request.user)
        return user_profile


class SellerPromoCRUDView(BaseCRUDView):
    permission_classes = [IsSeller & IsOwnerOrAdmin & IsVerified]
    serializer = SellersPromoSerializer
    model = SellerPromoModel

    def profile_getter(self, request):
        user_profile = AutoSellerModel.objects.get(user=request.user)
        return user_profile


class OffersForDealersView(viewsets.ViewSet):
    permission_classes = [IsDealer & IsVerified]

    def list(self, request):
        offers = OfferModel.objects.filter(is_active=True)
        serialized_offers = OffersSerializer(offers, many=True)
        return Response(serialized_offers.data)

    def retrieve(self, request, id=None):
        offer = OfferModel.objects.filter(id=id, is_active=True)
        serialized_offer = OffersSerializer(offer)
        return Response(serialized_offer.data)


class OffersCRUDView(BaseCRUDView):
    permission_classes = [IsBuyer & IsOwnerOrAdmin & IsVerified]
    serializer = OffersSerializer
    model = OfferModel

    def profile_getter(self, request):
        user_profile = CarBuyerModel.objects.get(user=request.user)
        return user_profile
