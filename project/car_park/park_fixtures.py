# pylint: disable=too-many-locals

"""This module contains fixtures for car_park tests"""

import uuid
from random import choice, randint

import pytest
from pytest import FixtureRequest
from user.models import AutoDealerModel, AutoSellerModel, CustomUserModel

from .models import (BaseCurrentCarParkModel, DealerCarParkModel,
                     SellerCarParkModel)
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


@pytest.fixture(scope='function', name='car_parks')
def create_car_parks(cars: list, all_profiles: dict) -> dict[str, BaseCurrentCarParkModel]:
    """Creates db records of car_parks of all types, returns dict of park owner
    type and their created car_park instance"""
    parks = {}
    creation_data_dict = {'dealer': {"profile": all_profiles['dealer'],
                                     "model": DealerCarParkModel,
                                     "serializer": DealerCarParkSerializer},
                          'seller': {"profile": all_profiles['seller'],
                                     "model": SellerCarParkModel,
                                     "serializer": SellersCarParkSerializer}}
    for owner_type, owner in creation_data_dict.items():
        park_data = {
            "car_model": choice(list(cars)),
            "available_number": randint(1, 10),
            "car_price": randint(1000, 10000),
            str(owner_type): owner["profile"]["profile_instance"]
        }
        parks[f'{owner_type}_park'] = owner['model'].objects.create(**park_data)
    return parks


@pytest.fixture(scope='function', name='car_park')
def create_user_car_park(cars: list,
                         all_profiles: dict,
                         request: FixtureRequest) -> dict[str, dict | BaseCurrentCarParkModel]:
    """Creates db record of car_park of passed user_type (dealer or seller) parameter,
    returns dict of created car_park instance and it's creation data"""
    creation_data_dict = {'dealer': {"profile": all_profiles['dealer']['profile_instance'],
                                     "model": DealerCarParkModel,
                                     "serializer": DealerCarParkSerializer},
                          'seller': {"profile": all_profiles['seller']['profile_instance'],
                                     "model": SellerCarParkModel,
                                     "serializer": SellersCarParkSerializer}}
    park_data = {
        "car_model": choice(list(cars)),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        str(request.param): creation_data_dict[str(request.param)]['profile']
    }
    park = creation_data_dict[str(request.param)]['model'].objects.create(**park_data)
    park_data = creation_data_dict[str(request.param)]['serializer'](park).data
    return {'park_instance': park,
            'park_data': park_data}


@pytest.fixture(scope='function', name='user_park')
def create_another_users_park(cars: list,
                              dealer_profile: dict,
                              seller_profile: dict,
                              request: FixtureRequest) -> dict[str,
                                                               dict | BaseCurrentCarParkModel]:
    """Creates new user and db record of car_park of passed user_type (dealer or seller)
    parameter, returns dict of created car_park instance and it's creation data"""
    user_data = {
        "username": f"test{uuid.uuid4().hex}",
        "password": f"pass{uuid.uuid4().hex}",
        "email": f"test{uuid.uuid4().hex}@am.com",
        "user_type": str.upper(request.param),
        "is_verified": True
    }
    user = CustomUserModel.objects.create_user(**user_data)
    profiles = {'dealer': dealer_profile, 'seller': seller_profile}
    profile_models = {'dealer': AutoDealerModel, 'seller': AutoSellerModel}
    profile = profiles[str(request.param)]
    profile['user'] = user
    profile = profile_models[str(request.param)].objects.create(**profile)
    models = {'dealer': DealerCarParkModel,
              'seller': SellerCarParkModel}
    serializers = {'dealer': DealerCarParkSerializer,
                   'seller': SellersCarParkSerializer}
    owner = profile
    park_data = {
        "car_model": choice(list(cars)),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        str(request.param): owner
    }
    park = models[str(request.param)].objects.create(**park_data)
    park_data = serializers[str(request.param)](park).data

    return {'park_instance': park,
            'park_data': park_data}
