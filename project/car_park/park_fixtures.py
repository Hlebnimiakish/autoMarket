import uuid
from random import choice, randint

import pytest
from user.models import AutoDealerModel, AutoSellerModel, CustomUserModel

from .models import DealerCarParkModel, SellerCarParkModel
from .serializers import DealerCarParkSerializer, SellersCarParkSerializer


@pytest.fixture(scope='function', name='car_parks')
def create_car_parks(cars, all_profiles):
    parks = {}
    creation_data_dict = {'dealer': {"profile": all_profiles['dealer'],
                                     "model": DealerCarParkModel,
                                     "serializer": DealerCarParkSerializer},
                          'seller': {"profile": all_profiles['seller'],
                                     "model": SellerCarParkModel,
                                     "serializer": SellersCarParkSerializer}}
    for owner_type, owner in creation_data_dict.items():
        park_data = {
            "car_model": choice([c for c in cars]),
            "available_number": randint(1, 10),
            "car_price": randint(1000, 10000),
            str(owner_type): owner["profile"]["profile_instance"]
        }
        park = owner['model'].objects.create(**park_data)
        parks[f'{owner_type}_park'] = park

    return parks


@pytest.fixture(scope='function', name='car_park')
def create_user_car_park(cars, all_profiles, request):
    creation_data_dict = {'dealer': {"profile": all_profiles['dealer']['profile_instance'],
                                     "model": DealerCarParkModel,
                                     "serializer": DealerCarParkSerializer},
                          'seller': {"profile": all_profiles['seller']['profile_instance'],
                                     "model": SellerCarParkModel,
                                     "serializer": SellersCarParkSerializer}}
    park_data = {
        "car_model": choice([c for c in cars]),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        str(request.param): creation_data_dict[str(request.param)]['profile']
    }
    park = creation_data_dict[str(request.param)]['model'].objects.create(**park_data)
    park_data = creation_data_dict[str(request.param)]['serializer'](park).data
    return {'park_instance': park,
            'park_data': park_data}


@pytest.fixture(scope='function', name='user_park')
def create_another_users_park(cars, dealer_profile, seller_profile, request):
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
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
        "car_model": choice([c for c in cars]),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        str(request.param): owner
    }
    park = models[str(request.param)].objects.create(**park_data)
    park_data = serializers[str(request.param)](park).data

    return {'park_instance': park,
            'park_data': park_data}
