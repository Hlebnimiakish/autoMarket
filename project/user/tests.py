import uuid
from random import choice

import pytest
from rest_framework.test import RequestsClient

BASE_URL = 'http://testserver/users/'

req = RequestsClient()

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('user_data',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_create_users_with_different_types(user_data):
    creation_response = req.post(f'{BASE_URL}registration/',
                                 json=user_data)
    assert creation_response.status_code == 201
    assert creation_response.json()['username'] == user_data['username']
    assert creation_response.json()['user_type'] == user_data['user_type']


@pytest.mark.parametrize('unverified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_user_can_read_update_delete_his_user_profile(unverified_user):
    view_user_response = req.get(f'{BASE_URL}my_user_page/',
                                 headers=unverified_user['headers'])
    assert view_user_response.status_code == 200
    assert view_user_response.json()['username'] == unverified_user['created_user']['username']
    unverified_user['created_user']['username'] = f'PreDelete{uuid.uuid4().hex}'
    update_user_response = req.put(f'{BASE_URL}my_user_page/',
                                   headers=unverified_user['headers'],
                                   json=unverified_user['created_user'])
    assert update_user_response.status_code == 200
    assert update_user_response.json()['username'] == unverified_user['created_user']['username']
    delete_response = req.delete(f'{BASE_URL}my_user_page/',
                                 headers=unverified_user['headers'])
    assert delete_response.status_code == 200


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_created_user_can_log_in_and_refresh(user_data):
    req.post(f'{BASE_URL}registration/', json=user_data)
    login_response = req.post(f'{BASE_URL}login/',
                              json=user_data)
    assert login_response.status_code == 200
    assert login_response.json()['access']
    refresh = login_response.json()['refresh']
    refr_response = req.post(f'{BASE_URL}login/refresh_token/',
                             json={'refresh': refresh})
    assert refr_response.status_code == 200
    assert refr_response.json()['access']


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_inactive_user_can_not_login_and_refresh(unverified_user):
    unverified_user['created_user']['is_active'] = False
    req.put(f'{BASE_URL}my_user_page/',
            headers=unverified_user['headers'],
            json=unverified_user['created_user'])
    login_response = req.post(f'{BASE_URL}login/',
                              json=unverified_user['creation_data'])
    assert login_response.status_code == 401


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_be_verified(unverified_user):
    id_data = {'user_id': unverified_user['created_user']['id']}
    verify = req.put(f'{BASE_URL}verification/',
                     json=id_data)
    assert verify.status_code == 200
    assert verify.json()['is_verified']


@pytest.mark.parametrize('unverified_user', ['DEALER'], indirect=True)
def test_unverified_users_can_not_create_profile(unverified_user, dealer_profile):
    create_profile_response = req.post(f'{BASE_URL}create_dealer_profile/',
                                       json=dealer_profile,
                                       headers=unverified_user['headers'])
    assert create_profile_response.status_code == 403


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_verified_users_can_create_profile(verified_user, dealer_profile):
    create_profile_response = req.post(f'{BASE_URL}create_dealer_profile/',
                                       json=dealer_profile,
                                       headers=verified_user['headers'])
    assert create_profile_response.status_code == 201


@pytest.mark.parametrize('verified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_users_with_different_types_can_create_only_corresponding_profile(verified_user,
                                                                          dealer_profile,
                                                                          seller_profile,
                                                                          buyer_profile):
    for user_type, profile in {'dealer': dealer_profile,
                               'seller': seller_profile,
                               'buyer': buyer_profile}.items():
        create_profile = req.post(f'{BASE_URL}create_{user_type}_profile/',
                                  json=profile,
                                  headers=verified_user['headers'])
        if user_type == str.lower(verified_user['created_user']['user_type']):
            assert create_profile.status_code == 201
            get_profile_response = req.get(f'{BASE_URL}my_{user_type}_profile/',
                                           headers=verified_user['headers'])
            assert get_profile_response.status_code == 200
        else:
            assert create_profile.status_code == 403


@pytest.mark.parametrize('verified_user',
                         ['DEALER', 'SELLER'],
                         indirect=True)
def test_dealer_seller_can_read_update_delete_his_type_profile(verified_user, request):
    user_type = str.lower(verified_user['created_user']['user_type'])
    user_profile = request.getfixturevalue(f'{user_type}_profile')
    req.post(f'{BASE_URL}create_{user_type}_profile/',
             json=user_profile,
             headers=verified_user['headers'])
    my_profile_response = req.get(f'{BASE_URL}my_{user_type}_profile/',
                                  headers=verified_user['headers'])
    assert my_profile_response.status_code == 200
    assert my_profile_response.json()['is_active']
    my_profile_response.json()['name'] = f'PreDelete{uuid.uuid4()}'
    profile_upd_response = req.put(f'{BASE_URL}my_{user_type}_profile/',
                                   headers=verified_user['headers'],
                                   json=my_profile_response.json())
    assert profile_upd_response.status_code == 200
    assert profile_upd_response.json()['name'] == \
           my_profile_response.json()['name']
    profile_del_response = req.delete(f'{BASE_URL}my_{user_type}_profile/',
                                      headers=verified_user['headers'])
    assert profile_del_response.status_code == 200


@pytest.mark.parametrize('verified_user',
                         ['BUYER'],
                         indirect=True)
def test_buyer_can_read_update_delete_his_type_profile(verified_user, request):
    user_type = str.lower(verified_user['created_user']['user_type'])
    user_profile = request.getfixturevalue(f'{user_type}_profile')
    req.post(f'{BASE_URL}create_{user_type}_profile/',
             json=user_profile,
             headers=verified_user['headers'])
    my_profile_response = req.get(f'{BASE_URL}my_{user_type}_profile/',
                                  headers=verified_user['headers'])
    assert my_profile_response.status_code == 200
    assert my_profile_response.json()['is_active']
    my_profile_response.json()['firstname'] = f'PreDelete{uuid.uuid4()}'
    profile_upd_response = req.put(f'{BASE_URL}my_{user_type}_profile/',
                                   headers=verified_user['headers'],
                                   json=my_profile_response.json())
    assert profile_upd_response.status_code == 200
    assert profile_upd_response.json()['firstname'] == \
           my_profile_response.json()['firstname']
    profile_del_response = req.delete(f'{BASE_URL}my_{user_type}_profile/',
                                      headers=verified_user['headers'])
    assert profile_del_response.status_code == 200


@pytest.mark.django_db
def test_dealer_can_view_other_users(all_users):
    dealer = all_users['dealer']

    # Dealers can view all other user profiles
    for user_type in all_users.keys():
        view_users = req.get(f'{BASE_URL}{user_type}s/',
                             headers=dealer['headers'])
        assert view_users.status_code == 200
        assert view_users.json()[0]['id']
        view_user = req.get(f'{BASE_URL}{user_type}s/1/',
                            headers=dealer['headers'])
        assert view_user.status_code == 200
        assert view_user.json()['id']


@pytest.mark.django_db
def test_buyer_can_view_other_users(all_users):
    buyer = all_users['buyer']

    # Buyers can't view seller and other buyer profiles
    for user_type in ['seller', 'buyer']:
        view_users = req.get(f'{BASE_URL}{user_type}s/',
                             headers=buyer['headers'])
        assert view_users.status_code == 403
        view_user = req.get(f'{BASE_URL}{user_type}s/1/',
                            headers=buyer['headers'])
        assert view_user.status_code == 403

    # Buyers can view dealer profiles
    view_dealers = req.get(f'{BASE_URL}dealers/',
                           headers=buyer['headers'])
    view_dealer = req.get(f'{BASE_URL}dealers/1/',
                          headers=buyer['headers'])
    assert view_dealer.status_code and view_dealers.status_code == 200
    assert view_dealer.json()['id'] and view_dealers.json()[0]['id']


@pytest.mark.django_db
def test_seller_can_view_other_users(all_users):
    buyer = all_users['seller']

    # Sellers can view dealers and other sellers profiles
    for user_type in ['seller', 'dealer']:
        view_users = req.get(f'{BASE_URL}{user_type}s/',
                             headers=buyer['headers'])
        assert view_users.status_code == 200
        assert view_users.json()[0]['id']
        view_user = req.get(f'{BASE_URL}{user_type}s/1/',
                            headers=buyer['headers'])
        assert view_user.status_code == 200
        assert view_user.json()['id']

    # Sellers can't view buyer profiles
    view_buyers = req.get(f'{BASE_URL}buyers/',
                          headers=buyer['headers'])
    view_buyer = req.get(f'{BASE_URL}buyers/1/',
                         headers=buyer['headers'])
    assert view_buyers.status_code and view_buyer.status_code == 403


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_invalid_data_tests(user_data, dealer_profile):
    user_data['user_type'] = 'ABRA_ABRA_CADABRA'
    creation_response = req.post(f'{BASE_URL}registration/',
                                 json=user_data)
    assert creation_response.status_code == 400

    user_data['user_type'] = 'DEALER'
    create_user_response = req.post(f'{BASE_URL}registration/',
                                    json=user_data)
    id_data = {'user_id': create_user_response.json()['id']}
    req.put(f'{BASE_URL}verification/', json=id_data)
    key = req.post(f'{BASE_URL}login/',
                   json=user_data).json()['access']
    headers = {
        'Authorization': f'Bearer {str(key)}'
    }
    dealer_profile['home_country'] = 'ABRA_ABRA_CADABRA'
    create_profile = req.post(f'{BASE_URL}create_dealer_profile/',
                              json=dealer_profile,
                              headers=headers)
    assert create_profile.status_code == 400

    user_data['email'] = 'ABRA_ABRA_CADABRA'
    get_key = req.post(f'{BASE_URL}login/',
                       json=user_data)
    assert get_key.status_code == 401
