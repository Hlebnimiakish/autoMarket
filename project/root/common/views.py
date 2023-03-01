from typing import Type

from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import filters, status, viewsets
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
    filterset_class: Type[FilterSet] | None = None
    filter_backends: tuple = (DjangoFilterBackend,)
    ordering_fields: list | None = None
    search_fields: list | None = None

    def get_filtered_objects_list(self, request: CustomRequest) -> QuerySet:
        if self.filterset_class:
            objects = self.filterset_class(data=request.query_params,
                                           queryset=self.model.objects.all(),
                                           request=request).qs
        else:
            objects = self.model.objects.all()
        if self.search_fields:
            search = filters.SearchFilter()
            objects = search.filter_queryset(request=request,
                                             queryset=objects,
                                             view=self)
        if self.ordering_fields:
            order = filters.OrderingFilter()
            objects = order.filter_queryset(request=request,
                                            queryset=objects,
                                            view=self)
        return objects

    def list(self, request: CustomRequest) -> Response:
        filtered_objects = self.get_filtered_objects_list(request)
        serialized_objs = self.serializer(filtered_objects,
                                          many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, pk: int) -> Response:
        obj = get_object_or_404(self.model.objects.all(), id=pk)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()


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

    def put(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        serialized_new_obj = self.serializer(data=request.data,
                                             instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def delete(self, request: CustomRequest) -> Response:
        obj = get_object_or_404(self.model.objects.all(),
                                **{self.user_data: self.profile_getter(request)})
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()


class BaseOwnModelReadView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    user_type: str
    user_model: Type[BaseModel | Model]
    filterset_class: Type[FilterSet] | None = None
    filter_backends: tuple = (DjangoFilterBackend,)
    ordering_fields: list | None = None
    search_fields: list | None = None

    def get_filtered_objects_list(self, request: CustomRequest) -> QuerySet:
        if self.filterset_class:
            objects = self.filterset_class(data=request.query_params,
                                           queryset=self.model.objects.all(),
                                           request=request).qs
        else:
            objects = self.model.objects.all()
        if self.search_fields:
            search = filters.SearchFilter()
            objects = search.filter_queryset(request=request,
                                             queryset=objects,
                                             view=self)
        if self.ordering_fields:
            order = filters.OrderingFilter()
            objects = order.filter_queryset(request=request,
                                            queryset=objects,
                                            view=self)
        return objects

    def profile_getter(self, request: CustomRequest) -> BaseModel | Model:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def list(self, request: CustomRequest) -> Response:
        profile = self.profile_getter(request)
        filtered_objects = self.get_filtered_objects_list(request)
        objs_set = filtered_objects.filter(**{self.user_type: profile})
        serialized_objs = self.serializer(objs_set, many=True)
        return Response(serialized_objs.data)

    def retrieve(self, request: CustomRequest, pk: int) -> Response:
        profile = self.profile_getter(request)
        objs_set = self.model.objects.filter(**{self.user_type: profile})
        obj = get_object_or_404(objs_set, id=pk)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()


class BaseCRUDView(viewsets.ViewSet):
    model: Type[BaseModel]
    serializer: Type[ModelSerializer]
    user_data: str
    user_model: Type[BaseModel | Model]
    filterset_class: Type[FilterSet] | None = None
    filter_backends: tuple = (DjangoFilterBackend,)
    ordering_fields: list | None = None
    search_fields: list | None = None

    def get_filtered_objects_list(self, request: CustomRequest) -> QuerySet:
        if self.filterset_class:
            objects = self.filterset_class(data=request.query_params,
                                           queryset=self.model.objects.all(),
                                           request=request).qs
        else:
            objects = self.model.objects.all()
        if self.search_fields:
            search = filters.SearchFilter()
            objects = search.filter_queryset(request=request,
                                             queryset=objects,
                                             view=self)
        if self.ordering_fields:
            order = filters.OrderingFilter()
            objects = order.filter_queryset(request=request,
                                            queryset=objects,
                                            view=self)
        return objects

    def profile_getter(self, request: CustomRequest) -> BaseModel | Model:
        user_profile = self.user_model.objects.get(user=request.user)
        return user_profile

    def retrieve(self, request: CustomRequest, pk: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=pk)
        serialized_obj = self.serializer(obj)
        return Response(serialized_obj.data)

    def update(self, request: CustomRequest, pk: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=pk)
        serialized_new_obj = self.serializer(data=request.data,
                                             instance=obj)
        serialized_new_obj.is_valid(raise_exception=True)
        serialized_new_obj.save()
        return Response(serialized_new_obj.data)

    def destroy(self, request: CustomRequest, pk: int) -> Response:
        objs_set = self.model.objects.filter(**{self.user_data: self.profile_getter(request)})
        obj = get_object_or_404(objs_set, id=pk)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_200_OK)

    def create(self, request: CustomRequest) -> Response:
        user_data = {self.user_data: self.profile_getter(request)}
        serialized_obj = self.serializer(data=request.data)
        serialized_obj.is_valid(raise_exception=True)
        serialized_obj.save(**user_data)
        return Response(serialized_obj.data, status=status.HTTP_201_CREATED)

    def list(self, request: CustomRequest) -> Response:
        filtered_objects = self.get_filtered_objects_list(request)
        objs = filtered_objects.filter(**{self.user_data: self.profile_getter(request)})
        serialized_objs = self.serializer(objs, many=True)
        return Response(serialized_objs.data)

    def get_serializer(self):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        return self.serializer()
