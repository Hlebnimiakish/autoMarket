import uuid
from random import randint

import pytest
from rest_framework.test import APIClient

from .models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                     CustomUserModel)
from .serializers import (AutoDealerSerializer, AutoSellerSerializer,
                          CarBuyerSerializer, CustomUserRUDSerializer)


@pytest.fixture(scope='session', name='client', autouse=True)
def get_client():
    return APIClient()


@pytest.fixture(scope='function')
def user_data(request):
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
def unverified_user(request, client):
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
def verified_user(request, client):
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
def create_all_user_types():
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
def create_all_users_profiles(all_users):
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL"
    }
    seller_profile_data = {
        "name": f"tseller{uuid.uuid4().hex}",
        "year_of_creation": randint(1000, 2023)
    }
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex)
    }
    profiles = {'dealer': dealer_profile_data,
                'seller': seller_profile_data,
                'buyer': buyer_profile_data}
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
def create_dealer_profile_data():
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL"
    }
    return dealer_profile_data


@pytest.fixture(scope='function', name='seller_profile')
def create_seller_profile_data():
    seller_profile_data = {
        "name": f"tseller{uuid.uuid4().hex}",
        "year_of_creation": randint(1000, 2023)
    }
    return seller_profile_data


@pytest.fixture(scope='function', name='buyer_profile')
def create_buyer_profile_data():
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex)
    }
    return buyer_profile_data
