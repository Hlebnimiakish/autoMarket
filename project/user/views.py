# mypy: disable-error-code=override

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.mixins import CreateModelMixin
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
                          CustomUserRUDSerializer, CustomUserSerializer)


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


class CustomUserCreationView(APIView):
    permission_classes = [IsNewUser]
    serializer = CustomUserSerializer
    model = CustomUserModel

    def post(self, request: CustomRequest):
        serialized_data = self.serializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        password = str(request.data.get("password"))
        try:
            validate_password(password=password)
        except ValidationError as ve:
            password_errors = dict()
            password_errors['password'] = ve
            return Response(data=password_errors)
        created_user = self.model.objects.create_user(**request.data)
        new_serialized_user = self.serializer(created_user)
        return Response(new_serialized_user.data, status=status.HTTP_201_CREATED)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()


class UserVerificationView(APIView):
    # This View probably will be changed in future
    # (when definite verification method will be picked)
    permission_classes = [IsNewUser]

    def put(self, request):
        user_id = request.data['user_id']
        user = CustomUserModel.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        serialized_upd_user = CustomUserSerializer(user)
        return Response(serialized_upd_user.data, status=status.HTTP_200_OK)


class SelfUserProfileRUDView(BaseOwnModelRUDView):
    permission_classes = [IsThisUser]
    serializer = CustomUserRUDSerializer
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
