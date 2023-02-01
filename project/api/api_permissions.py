# mypy: disable-error-code=override

from rest_framework import permissions
from rest_framework.request import Request
from user_app.models import CustomUserModel


class CustomUserRequest(Request):
    user: CustomUserModel


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user and request.user.is_staff:
            return True
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'dealer'):
            return obj.dealer == request.user
        elif hasattr(obj, 'seller'):
            return obj.seller == request.user
        elif hasattr(obj, 'buyer'):
            return obj.buyer == request.user
        elif hasattr(obj, 'creator'):
            return obj.creator == request.user
        return False


class IsDealer(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        if request.user.user_type == 'DEALER' or bool(request.user and request.user.is_staff):
            return True
        return False

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user.user_type == 'DEALER' or bool(request.user and request.user.is_staff):
            return True
        return False


class IsSeller(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        if request.user.user_type == 'SELLER' or bool(request.user and request.user.is_staff):
            return True
        return False

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user.user_type == 'SELLER' or bool(request.user and request.user.is_staff):
            return True
        return False


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request: CustomUserRequest, view) -> bool:
        if request.user.user_type == 'BUYER' or bool(request.user and request.user.is_staff):
            return True
        return False

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user.user_type == 'BUYER' or bool(request.user and request.user.is_staff):
            return True
        return False


class IsThisUser(permissions.BasePermission):
    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user == obj.id:
            return True
        return False


class IsVerified(permissions.BasePermission):
    message = "You have to be verified to perform this action."

    def has_permission(self, request: CustomUserRequest, view) -> bool:
        if request.user.is_verified:
            return True
        return False

    def has_object_permission(self, request: CustomUserRequest, view, obj) -> bool:
        if request.user.is_verified:
            return True
        return False
