import uuid
from random import randint

import pytest
from rest_framework.test import RequestsClient

pytestmark = pytest.mark.django_db

req = RequestsClient()

BASE_URL = 'http://testserver/users/'


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
    create_user_response = req.post(f'{BASE_URL}registration/',
                                    json=user_data)
    key = req.post(f'{BASE_URL}login/',
                   json=user_data).json()['access']
    headers = {
        'Authorization': f'Bearer {str(key)}'
    }
    yield {'created_user': create_user_response.json(),
           'creation_data': user_data,
           'headers': headers}

    req.delete(f'{BASE_URL}my_user_page/',
               headers=headers)


@pytest.fixture(scope='function')
def verified_user(request):
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": str(request.param)
    }
    create_user_response = req.post(f'{BASE_URL}registration/',
                                    json=user_data)
    key = req.post(f'{BASE_URL}login/',
                   json=user_data).json()['access']
    headers = {
        'Authorization': f'Bearer {str(key)}'
    }
    id_data = {'user_id': create_user_response.json()['id']}
    verify_response = req.put(f'{BASE_URL}verification/', json=id_data)
    yield {'created_user': verify_response.json(),
           'creation_data': user_data,
           'headers': headers}

    req.delete(f'{BASE_URL}my_user_page/',
               headers=headers)


@pytest.fixture(scope='package', name='all_users', autouse=True)
def create_all_user_types_with_profiles(django_db_setup, django_db_blocker):
    del django_db_setup
    with django_db_blocker.unblock():
        created_users = {}
        for user_type in ['DEALER', 'SELLER', 'BUYER']:
            password = uuid.uuid4().hex
            filler = uuid.uuid4().hex
            user_data = {
                "username": f"test{filler}",
                "password": f"pass{password}",
                "email": f"test{filler}@am.com",
                "user_type": user_type
            }
            create_user_response = req.post(f'{BASE_URL}registration/',
                                            json=user_data)
            key = req.post(f'{BASE_URL}login/',
                           json=user_data).json()['access']
            headers = {
                'Authorization': f'Bearer {str(key)}'
            }
            id_data = {'user_id': create_user_response.json()['id']}
            req.put(f'{BASE_URL}verification/', json=id_data)
            created_users[str.lower(user_type)] = {
                'created_user_data': create_user_response.json(),
                'headers': headers,
                'creation_data': user_data
            }
        yield created_users

        for user in created_users.values():
            req.delete(f'{BASE_URL}my_user_page/',
                       headers=user['headers'])


@pytest.fixture(scope='package', name='all_profiles', autouse=True)
def create_all_users_profiles(all_users, django_db_setup, django_db_blocker):
    del django_db_setup
    with django_db_blocker.unblock():
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
        all_profiles = {}
        for user_type in all_users.keys():
            create_profile = req.post(f'{BASE_URL}create_{user_type}_profile/',
                                      json=profiles[f'{user_type}'],
                                      headers=all_users[f'{user_type}']['headers'])
            all_profiles[user_type] = create_profile.json()
        yield all_profiles

        for user_type, user in all_users.items():
            req.delete(f'{BASE_URL}my_{user_type}_profile/',
                       headers=user['headers'])


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
