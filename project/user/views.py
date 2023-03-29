# mypy: disable-error-code=override
# pylint: skip-file

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
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
from .profile_filter import AutoDealerFilter
from .serializers import (AutoDealerFrontSerializer, AutoDealerSerializer,
                          AutoSellerFrontSerializer, AutoSellerSerializer,
                          CarBuyerFrontSerializer, CarBuyerSerializer,
                          CustomUserRUDSerializer, CustomUserSerializer)


def token_link_generator(user: CustomUserModel, request: CustomRequest,
                         url_name: str, token_name_prefix: str) -> str:
    """Generates and returns link for user to go to perform special actions
    requiring additional token verification"""
    generate_token = default_token_generator.make_token(user=user)
    host = request.get_host()
    token_link = \
        f'{host}{reverse(url_name)}?user_id={user.pk}' \
        f'&{token_name_prefix}_token={generate_token}'
    return token_link


def user_verification_mail_sender(user: CustomUserModel,
                                  request: CustomRequest):
    """Sends email with generated special link to perform requested user
    verification with email confirmation"""
    action_type = 'verification'
    verification_link = \
        token_link_generator(user, request, action_type, action_type)
    send_mail('Auto market user verification email',
              f'\nHello, {user.username}.'
              f'\nWe are glad to greet you at our auto market app.'
              f'\nPlease, verify your email by the next link:'
              f'\n{verification_link}'
              f'\nThank you for joining us!',
              'auto_market@email.com',
              [f'{user.email}'],
              fail_silently=False)


def password_reset_mail_sender(user: CustomUserModel, request: CustomRequest):
    """Sends email with generated special link to perform requested user
    password change with email confirmation"""
    password_reset_link = \
        token_link_generator(user, request, 'password-reset', 'password_reset')
    send_mail('Auto market password reset email',
              f'\nHello, {user.username}.'
              f'\nWe have got your password reset request.'
              f'\nPlease, follow the link to set a new password:'
              f'\n{password_reset_link}'
              f'\nIf u have not sent any password reset requests just ignore this email.'
              f'\nThank you!',
              'auto_market@email.com',
              [f'{user.email}'],
              fail_silently=False)


class BaseOwnProfileRUDView(BaseOwnModelRUDView):
    user_model: CustomUserModel = CustomUserModel  # type: ignore[assignment]
    user_data = 'user'

    def profile_getter(self, request: CustomRequest) -> CustomUserModel:
        user = self.user_model.objects.get(id=request.user.pk)
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
        user_verification_mail_sender(created_user, request)
        return Response(new_serialized_user.data, status=status.HTTP_201_CREATED)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()


class UserVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: CustomRequest):
        user_id = request.query_params.get('user_id', None)
        verification_token = request.query_params.get('verification_token', None)
        if user_id and verification_token:
            try:
                user = CustomUserModel.objects.get(id=user_id)
            except CustomUserModel.DoesNotExist:
                return Response('User not found', status=status.HTTP_404_NOT_FOUND)
            if default_token_generator.check_token(user, verification_token):
                user.is_verified = True
                user.save()
                serialized_upd_user = CustomUserSerializer(user)
                return Response(serialized_upd_user.data, status=status.HTTP_200_OK)
            return Response('Given token is invalid or out of date.',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('User id or verification token was not provided',
                        status=status.HTTP_400_BAD_REQUEST)


class SelfUserProfileRUDView(BaseOwnModelRUDView):
    permission_classes = [IsThisUser]
    serializer = CustomUserRUDSerializer
    model: CustomUserModel = CustomUserModel  # type: ignore[assignment]
    user_data = 'id'

    def profile_getter(self, request: CustomRequest) -> int:
        id = request.user.pk
        return id


class UserPasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def put(self, request: CustomRequest):
        email = str(request.data.get('email'))
        try:
            user = CustomUserModel.objects.get(email=email)
            password_reset_mail_sender(user, request)
            return Response('Password reset link have been sent to given email',
                            status=status.HTTP_200_OK)
        except CustomUserModel.DoesNotExist:
            return Response("User with given email wasn't found",
                            status=status.HTTP_404_NOT_FOUND)


class UserPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def put(self, request: CustomRequest):
        user_id = request.query_params.get('user_id', None)
        password_reset_token = request.query_params.get('password_reset_token', None)
        if user_id and password_reset_token:
            try:
                user = CustomUserModel.objects.get(id=user_id)
            except CustomUserModel.DoesNotExist:
                return Response('User not found', status=status.HTTP_404_NOT_FOUND)
            if default_token_generator.check_token(user, password_reset_token):
                old_password = str(request.data.get('old_password'))
                new_password = str(request.data.get('new_password'))
                if user.check_password(old_password):
                    try:
                        validate_password(password=new_password)
                    except ValidationError as ve:
                        password_errors = dict()
                        password_errors['password'] = ve
                        return Response(data=password_errors,
                                        status=status.HTTP_400_BAD_REQUEST)
                    user.set_password(new_password)
                    user.save()
                    return Response('Password was successfully changed!',
                                    status=status.HTTP_200_OK)
                return Response('Given old password is incorrect',
                                status=status.HTTP_400_BAD_REQUEST)
            return Response('Given token is invalid or out of date.',
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('User id or password reset token was not provided',
                        status=status.HTTP_400_BAD_REQUEST)


class AutoDealerReadOnlyView(BaseReadOnlyView):
    serializer = AutoDealerFrontSerializer
    model = AutoDealerModel
    filterset_class = AutoDealerFilter
    filter_backends = (filters.SearchFilter,
                       filters.OrderingFilter,
                       DjangoFilterBackend,)
    search_fields = ['name']


class AutoSellerReadOnlyView(BaseReadOnlyView):
    permission_classes = [IsSeller & IsVerified | IsDealer & IsVerified]
    serializer = AutoSellerFrontSerializer
    model = AutoSellerModel
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']
    ordering_fields = ['year_of_creation']


class CarBuyerReadOnlyView(BaseReadOnlyView):
    permission_classes = [IsDealer & IsVerified]
    serializer = CarBuyerFrontSerializer
    model = CarBuyerModel
    filter_backends = (filters.SearchFilter,)
    search_fields = ['drivers_license_number', 'firstname', 'lastname']


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
