# pylint: disable=redefined-outer-name, duplicate-code

"""This module contains fixtures for user tests"""

import uuid
from random import randint

import pytest
from pytest import FixtureRequest
from rest_framework.test import APIClient

from .models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                     CustomUserModel)
from .serializers import (AutoDealerSerializer, AutoSellerSerializer,
                          CarBuyerSerializer, CustomUserRUDSerializer)


@pytest.fixture(scope='function')
def user_data(request: FixtureRequest) -> dict:
    """Creates and returns dict of required
     user data"""
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": str(request.param)
    }
    return user_data


@pytest.fixture(scope='function')
def unverified_user(request: FixtureRequest, client: APIClient) -> dict[str,
                                                                        dict | CustomUserModel]:
    """Creates db record of unverified user of passed in parameter
    user_type and returns dict of user data and created user
    instance, authenticate created user"""
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": str(request.param)
    }
    user = CustomUserModel.objects.create_user(**user_data)
    created_user = CustomUserRUDSerializer(user).data
    client.force_authenticate(user=user)
    return {'created_user_data': created_user,
            'user_instance': user}


@pytest.fixture(scope='function')
def verified_user(request: FixtureRequest, client: APIClient) -> dict[str,
                                                                      dict | CustomUserModel]:
    """Creates db record of verified user of passed in parameter
    user_type and returns dict of user data and created user
    instance, authenticate created user"""
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": str(request.param),
        "is_verified": True
    }
    user = CustomUserModel.objects.create_user(**user_data)
    created_user = CustomUserRUDSerializer(user).data
    client.force_authenticate(user=user)
    return {'created_user_data': created_user,
            'user_instance': user}


@pytest.fixture(scope='function', name='all_users')
def create_all_user_types() -> dict[str, dict[str,
                                              dict | CustomUserModel]]:
    """Creates db records of verified users of all user_types
    and returns dict of user_types and their user data and
    created user instance"""
    created_users = {}
    for user_type in ['DEALER', 'SELLER', 'BUYER']:
        password = uuid.uuid4().hex
        filler = uuid.uuid4().hex
        user_data = {
            "username": f"test{filler}",
            "password": f"pass{password}",
            "email": f"test{filler}@am.com",
            "user_type": str(user_type),
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        created_user = CustomUserRUDSerializer(user).data
        created_users[str.lower(user_type)] = {
            'created_user_data': created_user,
            'user_instance': user
        }
    return created_users


@pytest.fixture(scope='function', name='all_profiles')
def create_all_users_profiles(all_users: dict,
                              dealer_profile: dict,
                              seller_profile: dict,
                              buyer_profile: dict) -> dict[str, dict[str,
                                                                     dict |
                                                                     AutoDealerModel |
                                                                     AutoSellerModel |
                                                                     CarBuyerModel]]:
    """Creates db records of profiles of all types and returns dict of
    user_types and their profile data and created profile instance"""
    profiles = {'dealer': dealer_profile,
                'seller': seller_profile,
                'buyer': buyer_profile}
    models = {'dealer': AutoDealerModel,
              'seller': AutoSellerModel,
              'buyer': CarBuyerModel}
    serializers = {'dealer': AutoDealerSerializer,
                   'seller': AutoSellerSerializer,
                   'buyer': CarBuyerSerializer}
    all_profiles = {}
    for user_type in all_users.keys():
        profiles[str(user_type)]['user'] = all_users[str(user_type)]['user_instance']
        profile = models[str(user_type)].objects.create(**profiles[str(user_type)])
        all_profiles[user_type] = {
            "profile_data": serializers[str(user_type)](profile).data,
            "profile_instance": profile
        }
    return all_profiles


@pytest.fixture(scope='function', name='dealer_profile')
def create_dealer_profile_data() -> dict:
    """Creates and returns a dict of required dealer profile data"""
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL",
        "balance": 100000
    }
    return dealer_profile_data


@pytest.fixture(scope='function', name='seller_profile')
def create_seller_profile_data() -> dict:
    """Creates and returns a dict of required seller profile data"""
    seller_profile_data = {
        "name": f"tseller{uuid.uuid4().hex}",
        "year_of_creation": randint(1000, 2023)
    }
    return seller_profile_data


@pytest.fixture(scope='function', name='buyer_profile')
def create_buyer_profile_data() -> dict:
    """Creates and returns a dict of required buyer profile data"""
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex),
        "balance": 100000
    }
    return buyer_profile_data


@pytest.fixture(scope='function', name='additional_profiles')
def create_additional_profiles() -> dict[str, dict[str,
                                                   dict |
                                                   AutoDealerModel |
                                                   AutoSellerModel |
                                                   CarBuyerModel]]:
    """Creates new users and db records of their profiles of all types and returns
    dict of user_types and their created profile instance and it's creation data"""
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL",
        "balance": 100000
    }
    seller_profile_data = {
        "name": f"tseller{uuid.uuid4().hex}",
        "year_of_creation": randint(1000, 2023)
    }
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex),
        "balance": 100000
    }
    profiles = {"DEALER": dealer_profile_data,
                "SELLER": seller_profile_data,
                "BUYER": buyer_profile_data}
    models = {'DEALER': AutoDealerModel,
              'SELLER': AutoSellerModel,
              'BUYER': CarBuyerModel}
    serializers = {'DEALER': AutoDealerSerializer,
                   'SELLER': AutoSellerSerializer,
                   'BUYER': CarBuyerSerializer}
    created_profiles = {}
    for user_type in ["DEALER", "SELLER", "BUYER"]:
        password = uuid.uuid4().hex
        filler = uuid.uuid4().hex
        user_data = {
            "username": f"test{filler}",
            "password": f"pass{password}",
            "email": f"test{filler}@am.com",
            "user_type": str(user_type),
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        profiles[str(user_type)]['user'] = user
        profile = models[str(user_type)].objects.create(**profiles[str(user_type)])
        profile_data = serializers[str(user_type)](profile).data
        created_profiles[str(user_type).lower()] = {"profile_instance": profile,
                                                    "profile_data": profile_data}
    return created_profiles
