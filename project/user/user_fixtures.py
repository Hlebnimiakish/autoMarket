import uuid
from random import randint

import pytest
from rest_framework.test import RequestsClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (AutoDealerModel, AutoSellerModel, CarBuyerModel,
                     CustomUserModel)
from .serializers import (AutoDealerSerializer, AutoSellerSerializer,
                          CarBuyerSerializer, CustomUserRUDSerializer)


@pytest.fixture(scope='session', name='client', autouse=True)
def get_request_client():
    return RequestsClient()


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
def unverified_user(request):
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
    tokens = RefreshToken.for_user(user)
    headers = {
        'Authorization': f'Bearer {str(tokens.access_token)}'
    }
    yield {'created_user': created_user,
           'creation_data': user_data,
           'headers': headers}

    user.delete()


@pytest.fixture(scope='function')
def verified_user(request):
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
    tokens = RefreshToken.for_user(user)
    headers = {
        'Authorization': f'Bearer {str(tokens.access_token)}'
    }
    yield {'created_user': created_user,
           'creation_data': user_data,
           'headers': headers}

    user.delete()


@pytest.fixture(scope='function', name='all_users')
def create_all_user_types_with_profiles():
    created_users = {}
    for user_type in ['DEALER', 'SELLER', 'BUYER']:
        password = uuid.uuid4().hex
        filler = uuid.uuid4().hex
        user_data = {
            "username": f"test{filler}",
            "password": f"pass{password}",
            "email": f"test{filler}@am.com",
            "user_type": user_type,
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        created_user = CustomUserRUDSerializer(user).data
        tokens = RefreshToken.for_user(user)
        headers = {
            'Authorization': f'Bearer {str(tokens.access_token)}'
        }
        created_users[str.lower(user_type)] = {
            'created_user_data': created_user,
            'headers': headers,
            'user_instance': user
        }
    yield created_users

    for user in created_users.values():
        user['user_instance'].delete()


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
    profiles_list = []
    for user_type in all_users.keys():
        model = models[f'{user_type}']
        user = all_users[f'{user_type}']['user_instance']
        profile = model.objects.create(user=user,
                                       **profiles[f'{user_type}'])
        profile_data = serializers[f'{user_type}'](profile).data
        all_profiles[user_type] = profile_data
        profiles_list.append(profile)
    yield all_profiles

    for p in profiles_list:
        p.delete()


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
