# mypy: disable-error-code=override

from car_spec.models import DealerSearchCarSpecificationModel
from discount.models import RegularCustomerDiscountLevelsModel
from rest_framework import permissions
from rest_framework.request import Request
from user.models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                         CustomUserModel)


class CustomUserRequest(Request):
    user: CustomUserModel


class UserHasNoProfile(permissions.BasePermission):
    message = 'You already have profile'

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return not bool(AutoDealerModel.objects.get_or_none(user=request.user) or
                        AutoSellerModel.objects.get_or_none(user=request.user) or
                        CarBuyerModel.objects.get_or_none(user=request.user))


class SellerHasNoDiscountSet(permissions.BasePermission):

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        seller = AutoSellerModel.objects.get_or_none(user=request.user)
        if seller:
            return not bool(RegularCustomerDiscountLevelsModel.objects.get_or_none(seller=seller))
        else:
            return False


class IsNewUser(permissions.BasePermission):
    message = 'You already have user profile'

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return not bool(request.user and CustomUserModel.objects.get_or_none(id=request.user.id))


class CurrentDealerHasNoSpec(permissions.BasePermission):
    message = 'You already have a specification'

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        user = request.user
        current_dealer = AutoDealerModel.objects.get(user=user)
        return not \
            bool(DealerSearchCarSpecificationModel.objects.get_or_none(dealer=current_dealer))


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user and bool(request.user.is_staff):
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'dealer'):
            return obj.dealer.user == request.user
        elif hasattr(obj, 'seller'):
            return obj.seller.user == request.user
        elif hasattr(obj, 'buyer'):
            return obj.buyer.user == request.user
        elif hasattr(obj, 'creator'):
            return obj.creator.user == request.user
        return False


class IsDealer(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return bool((request.user and request.user.user_type == 'DEALER') or
                    (request.user and request.user.is_staff))

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        return bool((request.user and request.user.user_type == 'DEALER') or
                    (request.user and request.user.is_staff))


class IsSeller(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return bool((request.user and request.user.user_type == 'SELLER') or
                    (request.user and request.user.is_staff))

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        return bool((request.user and request.user.user_type == 'SELLER') or
                    (request.user and request.user.is_staff))


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return bool((request.user and request.user.user_type == 'BUYER')
                    or (request.user and request.user.is_staff))

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        return bool((request.user and request.user.user_type == 'BUYER')
                    or (request.user and request.user.is_staff))


class IsThisUser(permissions.BasePermission):
    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        return bool(request.user == obj.id)


class IsVerified(permissions.BasePermission):
    message = "You have to be verified to perform this action."

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        return bool(request.user.is_verified)

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        return bool(request.user.is_verified)
