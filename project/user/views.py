# mypy: disable-error-code=override

from django.contrib.auth import login, logout
from rest_framework import generics, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from root.common.permissions import (IsBuyer, IsDealer, IsNewUser,
                                     IsOwnerOrAdmin, IsSeller, IsThisUser,
                                     IsVerified, UserHasNoProfile)
from root.common.views import (BaseOwnModelRUDView, BaseReadOnlyView,
                               CustomRequest)

from .models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                     CustomUserModel)
from .serializers import (AutoDealerFrontSerializer, AutoDealerSerializer,
                          AutoSellerFrontSerializer, AutoSellerSerializer,
                          CarBuyerFrontSerializer, CarBuyerSerializer,
                          CustomUserSerializer)


class BaseOwnProfileRUDView(BaseOwnModelRUDView):
    user_model: CustomUserModel = CustomUserModel  # type: ignore[assignment]
    user_data = 'user'

    def profile_getter(self, request: CustomRequest) -> CustomUserModel:
        user = self.user_model.objects.get(id=request.user.id)
        return user


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
    permission_classes = [IsNewUser]
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
    serializer = CarBuyerFrontSerializer
    model = CarBuyerModel


class AutoDealerCreateView(BaseProfileCreationView):
    permission_classes = [IsDealer & IsVerified & UserHasNoProfile]
    serializer_class = AutoDealerSerializer


class CarBuyerCreateView(BaseProfileCreationView):
    permission_classes = [IsBuyer & IsVerified & UserHasNoProfile]
    serializer_class = CarBuyerSerializer


class AutoSellerCreateView(BaseProfileCreationView):
    permission_classes = [IsSeller & IsVerified & UserHasNoProfile]
    serializer_class = AutoSellerSerializer


class AutoDealerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoDealerSerializer
    model = AutoDealerModel


class CarBuyerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = CarBuyerSerializer
    model = CarBuyerModel


class AutoSellerRUDView(BaseOwnProfileRUDView):
    permission_classes = [IsOwnerOrAdmin]
    serializer = AutoSellerSerializer
    model = AutoSellerModel
