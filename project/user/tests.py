import uuid
from random import choice

import pytest

BASE_URL = 'http://testserver/users/'

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('user_data',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_create_users_with_different_types(user_data, client):
    response = client.post(f'{BASE_URL}registration/',
                           json=user_data)
    assert response.status_code == 201
    assert response.json()['username'] == user_data['username']
    assert response.json()['user_type'] == user_data['user_type']


@pytest.mark.parametrize('unverified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_user_can_read_update_delete_his_user_profile(unverified_user, client):
    response = client.get(f'{BASE_URL}my_user_page/',
                          headers=unverified_user['headers'])
    assert response.status_code == 200
    assert response.json()['username'] == unverified_user['created_user']['username']
    unverified_user['created_user']['username'] = f'PreDelete{uuid.uuid4().hex}'
    response = client.put(f'{BASE_URL}my_user_page/',
                          headers=unverified_user['headers'],
                          json=unverified_user['created_user'])
    assert response.status_code == 200
    assert response.json()['username'] == unverified_user['created_user']['username']
    response = client.delete(f'{BASE_URL}my_user_page/',
                             headers=unverified_user['headers'])
    assert response.status_code == 200


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_created_user_can_log_in_and_refresh(user_data, client):
    client.post(f'{BASE_URL}registration/', json=user_data)
    response = client.post(f'{BASE_URL}login/',
                           json=user_data)
    refresh = response.json()['refresh']
    assert response.status_code == 200
    assert response.json()['access']
    response = client.post(f'{BASE_URL}login/refresh_token/',
                           json={'refresh': refresh})
    assert response.status_code == 200
    assert response.json()['access']


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_inactive_user_can_not_login_and_refresh(unverified_user, client):
    unverified_user['created_user']['is_active'] = False
    client.put(f'{BASE_URL}my_user_page/',
               headers=unverified_user['headers'],
               json=unverified_user['created_user'])
    response = client.post(f'{BASE_URL}login/',
                           json=unverified_user['creation_data'])
    assert response.status_code == 401


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_be_verified(unverified_user, client):
    id_data = {'user_id': unverified_user['created_user']['id']}
    response = client.put(f'{BASE_URL}verification/',
                          json=id_data)
    assert response.status_code == 200
    assert response.json()['is_verified']


@pytest.mark.parametrize('unverified_user', ['DEALER'], indirect=True)
def test_unverified_users_can_not_create_profile(unverified_user, dealer_profile, client):
    response = client.post(f'{BASE_URL}create_dealer_profile/',
                           json=dealer_profile,
                           headers=unverified_user['headers'])
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_verified_users_can_create_profile(verified_user, dealer_profile, client):
    response = client.post(f'{BASE_URL}create_dealer_profile/',
                           json=dealer_profile,
                           headers=verified_user['headers'])
    assert response.status_code == 201


@pytest.mark.parametrize('verified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_users_with_different_types_can_create_only_corresponding_profile(verified_user,
                                                                          dealer_profile,
                                                                          seller_profile,
                                                                          buyer_profile,
                                                                          client):
    for user_type, profile in {'dealer': dealer_profile,
                               'seller': seller_profile,
                               'buyer': buyer_profile}.items():
        response = client.post(f'{BASE_URL}create_{user_type}_profile/',
                               json=profile,
                               headers=verified_user['headers'])
        if user_type == str.lower(verified_user['created_user']['user_type']):
            assert response.status_code == 201
            response = client.get(f'{BASE_URL}my_{user_type}_profile/',
                                  headers=verified_user['headers'])
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.parametrize('verified_user',
                         ['DEALER', 'SELLER'],
                         indirect=True)
def test_dealer_seller_can_read_update_delete_his_type_profile(verified_user,
                                                               request,
                                                               client):
    user_type = str.lower(verified_user['created_user']['user_type'])
    profile_data = request.getfixturevalue(f'{user_type}_profile')
    client.post(f'{BASE_URL}create_{user_type}_profile/',
                json=profile_data,
                headers=verified_user['headers'])
    response = client.get(f'{BASE_URL}my_{user_type}_profile/',
                          headers=verified_user['headers'])
    assert response.status_code == 200
    assert response.json()['is_active']
    profile_data = response.json()
    profile_data['name'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(f'{BASE_URL}my_{user_type}_profile/',
                          headers=verified_user['headers'],
                          json=profile_data)
    assert response.status_code == 200
    assert profile_data['name'] == response.json()['name']
    response = client.delete(f'{BASE_URL}my_{user_type}_profile/',
                             headers=verified_user['headers'])
    assert response.status_code == 200


@pytest.mark.parametrize('verified_user',
                         ['BUYER'],
                         indirect=True)
def test_buyer_can_read_update_delete_his_type_profile(verified_user,
                                                       request,
                                                       client):
    user_type = str.lower(verified_user['created_user']['user_type'])
    user_profile = request.getfixturevalue(f'{user_type}_profile')
    client.post(f'{BASE_URL}create_{user_type}_profile/',
                json=user_profile,
                headers=verified_user['headers'])
    response = client.get(f'{BASE_URL}my_{user_type}_profile/',
                          headers=verified_user['headers'])
    assert response.status_code == 200
    assert response.json()['is_active']
    profile_data = response.json()
    profile_data['firstname'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(f'{BASE_URL}my_{user_type}_profile/',
                          headers=verified_user['headers'],
                          json=profile_data)
    assert response.status_code == 200
    assert profile_data['firstname'] == response.json()['firstname']
    response = client.delete(f'{BASE_URL}my_{user_type}_profile/',
                             headers=verified_user['headers'])
    assert response.status_code == 200


@pytest.mark.django_db
def test_dealer_can_view_other_users(all_users, all_profiles, client):
    dealer = all_users['dealer']

    # Dealers can view all other user profiles
    for user_type in all_users.keys():
        response = client.get(f'{BASE_URL}{user_type}s/',
                              headers=dealer['headers'])
        assert response.status_code == 200
        assert response.json()[0]['id']
        response = client.get(f'{BASE_URL}{user_type}s/1/',
                              headers=dealer['headers'])
        assert response.status_code == 200
        assert response.json()['id']


@pytest.mark.django_db
def test_buyer_can_view_other_users(all_users, all_profiles, client):
    buyer = all_users['buyer']

    # Buyers can't view seller and other buyer profiles
    for user_type in ['seller', 'buyer']:
        response = client.get(f'{BASE_URL}{user_type}s/',
                              headers=buyer['headers'])
        assert response.status_code == 403
        response = client.get(f'{BASE_URL}{user_type}s/1/',
                              headers=buyer['headers'])
        assert response.status_code == 403

    # Buyers can view dealer profiles
    response = client.get(f'{BASE_URL}dealers/',
                          headers=buyer['headers'])
    assert response.status_code == 200
    assert response.json()[0]['id']
    response = client.get(f'{BASE_URL}dealers/1/',
                          headers=buyer['headers'])
    assert response.status_code == 200
    assert response.json()['id']


@pytest.mark.django_db
def test_seller_can_view_other_users(all_users, all_profiles, client):
    buyer = all_users['seller']

    # Sellers can view dealers and other sellers profiles
    for user_type in ['seller', 'dealer']:
        response = client.get(f'{BASE_URL}{user_type}s/',
                              headers=buyer['headers'])
        assert response.status_code == 200
        assert response.json()[0]['id']
        response = client.get(f'{BASE_URL}{user_type}s/1/',
                              headers=buyer['headers'])
        assert response.status_code == 200
        assert response.json()['id']

    # Sellers can't view buyer profiles
    response = client.get(f'{BASE_URL}buyers/',
                          headers=buyer['headers'])
    assert response.status_code == 403
    response = client.get(f'{BASE_URL}buyers/1/',
                          headers=buyer['headers'])
    assert response.status_code == 403


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_invalid_data_tests(user_data, dealer_profile, client):
    user_data['user_type'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{BASE_URL}registration/',
                           json=user_data)
    assert response.status_code == 400

    user_data['user_type'] = 'DEALER'
    response = client.post(f'{BASE_URL}registration/',
                           json=user_data)
    id_data = {'user_id': response.json()['id']}
    client.put(f'{BASE_URL}verification/', json=id_data)
    key = client.post(f'{BASE_URL}login/',
                      json=user_data).json()['access']
    headers = {
        'Authorization': f'Bearer {str(key)}'
    }
    dealer_profile['home_country'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{BASE_URL}create_dealer_profile/',
                           json=dealer_profile,
                           headers=headers)
    assert response.status_code == 400

    user_data['email'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{BASE_URL}login/',
                           json=user_data)
    assert response.status_code == 401
