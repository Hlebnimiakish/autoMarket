from typing import Type

from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from user.models import BaseModel, CustomUserModel


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
