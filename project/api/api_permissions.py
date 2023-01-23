from rest_framework import permissions


class SafeOrIsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user or bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
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


class IsDealer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'DEALER' or bool(request.user and request.user.is_staff):
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'DEALER' or bool(request.user and request.user.is_staff):
            return True


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'SELLER' or bool(request.user and request.user.is_staff):
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'SELLER' or bool(request.user and request.user.is_staff):
            return True


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.user_type == 'BUYER' or bool(request.user and request.user.is_staff):
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'BUYER' or bool(request.user and request.user.is_staff):
            return True


class IsThisUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.id:
            return True


class IsVerified(permissions.BasePermission):
    message = "You have to be verified to perform this action."

    def has_permission(self, request, view):
        if request.user.is_verified:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_verified:
            return True
