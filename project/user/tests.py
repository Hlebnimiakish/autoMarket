import uuid
from random import choice

import pytest
from django.urls import reverse

BASE_URL = 'http://testserver'

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('user_data',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_create_users_with_different_types(user_data, client):
    response = client.post(f'{reverse("registration")}',
                           data=user_data,
                           format='json')
    assert response.status_code == 201
    assert response.data['username'] == user_data['username']
    assert response.data['user_type'] == user_data['user_type']


@pytest.mark.parametrize('unverified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_user_can_read_update_delete_his_user_profile(unverified_user, client):
    response = client.get(f'{reverse("user")}',
                          format='json')
    assert response.status_code == 200
    assert response.data['username'] == unverified_user['created_user_data']['username']
    unverified_user['created_user_data']['username'] = f'PreDelete{uuid.uuid4().hex}'
    response = client.put(f'{reverse("user")}',
                          data=unverified_user['created_user_data'],
                          format='json')
    assert response.status_code == 200
    assert response.data['username'] == unverified_user['created_user_data']['username']
    response = client.delete(f'{reverse("user")}',
                             format='json')
    assert response.status_code == 200


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_created_user_can_log_in_and_refresh(user_data, client):
    client.post(f'{reverse("registration")}', data=user_data, format='json')
    response = client.post(f'{reverse("get-token")}',
                           data=user_data,
                           format='json')
    refresh = response.data['refresh']
    assert response.status_code == 200
    assert response.data['access']
    response = client.post(f'{reverse("refresh-token")}',
                           data={'refresh': refresh},
                           format='json')
    assert response.status_code == 200
    assert response.data['access']


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_inactive_user_can_not_login_and_refresh(user_data, client):
    user_data['is_active'] = False
    client.post(f'{reverse("registration")}', data=user_data, format='json')
    user_data['is_active'] = True
    response = client.post(f'{reverse("get-token")}',
                           data=user_data,
                           format='json')
    assert response.status_code == 401


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_be_verified(unverified_user, client):
    id_data = {'user_id': unverified_user['created_user_data']['id']}
    response = client.put(f'{reverse("verification")}',
                          data=id_data,
                          format='json')
    assert response.status_code == 200
    assert response.data['is_verified']


@pytest.mark.parametrize('unverified_user', ['DEALER'], indirect=True)
def test_unverified_users_can_not_create_profile(unverified_user, dealer_profile, client):
    response = client.post(f'{reverse("dealer-creation")}',
                           data=dealer_profile,
                           format='json')
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_verified_users_can_create_profile(verified_user, dealer_profile, client):
    response = client.post(f'{reverse("dealer-creation")}',
                           data=dealer_profile,
                           format='json')
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
        url_name = f'{user_type}-creation'
        response = client.post(f'{reverse(url_name)}',
                               data=profile,
                               format='json')
        if user_type == str.lower(verified_user['created_user_data']['user_type']):
            assert response.status_code == 201
            url_name = f'{user_type}-profile'
            response = client.get(f'{reverse(url_name)}')
            assert response.status_code == 200
        else:
            assert response.status_code == 403


@pytest.mark.parametrize('verified_user',
                         ['DEALER', 'SELLER'],
                         indirect=True)
def test_dealer_seller_can_read_update_delete_his_type_profile(verified_user,
                                                               request,
                                                               client):
    user_type = str.lower(verified_user['created_user_data']['user_type'])
    profile_data = request.getfixturevalue(f'{user_type}_profile')
    url_name = f'{user_type}-creation'
    client.post(f'{reverse(url_name)}',
                data=profile_data,
                format='json')
    url_name = f'{user_type}-profile'
    response = client.get(f'{reverse(url_name)}')
    assert response.status_code == 200
    assert response.data['is_active']
    profile_data = response.data
    profile_data['name'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(f'{reverse(url_name)}',
                          data=profile_data,
                          format='json')
    assert response.status_code == 200
    assert profile_data['name'] == response.data['name']
    response = client.delete(f'{reverse(url_name)}')
    assert response.status_code == 200


@pytest.mark.parametrize('verified_user',
                         ['BUYER'],
                         indirect=True)
def test_buyer_can_read_update_delete_his_type_profile(verified_user,
                                                       request,
                                                       client):
    user_type = str.lower(verified_user['created_user_data']['user_type'])
    user_profile = request.getfixturevalue(f'{user_type}_profile')
    client.post(f'{reverse("buyer-creation")}',
                data=user_profile,
                format='json')
    response = client.get(f'{reverse("buyer-profile")}')
    assert response.status_code == 200
    assert response.data['is_active']
    profile_data = response.data
    profile_data['firstname'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(f'{reverse("buyer-profile")}',
                          data=profile_data,
                          format='json')
    assert response.status_code == 200
    assert profile_data['firstname'] == response.data['firstname']
    response = client.delete(f'{reverse("buyer-profile")}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_dealer_can_view_other_users(all_users, all_profiles, client):
    dealer = all_users['dealer']
    client.force_authenticate(user=dealer['user_instance'])

    # Dealers can view all other user profiles
    for user_type in all_users.keys():
        url_name = f'{user_type}-list'
        response = client.get(f'{reverse(url_name)}')
        assert response.status_code == 200
        assert response.data[0]['id']
        url_name = f'{user_type}-detail'
        response = client.get(f'{reverse(url_name, kwargs={"pk": 1})}')
        assert response.status_code == 200
        assert response.data['id']


@pytest.mark.django_db
def test_buyer_can_view_other_users(all_users, all_profiles, client):
    buyer = all_users['buyer']
    client.force_authenticate(user=buyer['user_instance'])

    # Buyers can't view seller and other buyer profiles
    for user_type in ['seller', 'buyer']:
        url_name = f'{user_type}-list'
        response = client.get(f'{reverse(url_name)}')
        assert response.status_code == 403
        url_name = f'{user_type}-detail'
        response = client.get(f'{reverse(url_name, kwargs={"pk": 1})}')
        assert response.status_code == 403

    # Buyers can view dealer profiles
    response = client.get(f'{reverse("dealer-list")}')
    assert response.status_code == 200
    assert response.data[0]['id']
    response = client.get(f'{reverse("dealer-detail", kwargs={"pk": 1})}')
    assert response.status_code == 200
    assert response.data['id']


@pytest.mark.django_db
def test_seller_can_view_other_users(all_users, all_profiles, client):
    seller = all_users['seller']
    client.force_authenticate(user=seller['user_instance'])

    # Sellers can view dealers and other sellers profiles
    for user_type in ['seller', 'dealer']:
        url_name = f'{user_type}-list'
        response = client.get(f'{reverse(url_name)}')
        assert response.status_code == 200
        assert response.data[0]['id']
        url_name = f'{user_type}-detail'
        response = client.get(f'{reverse(url_name, kwargs={"pk": 1})}')
        assert response.status_code == 200
        assert response.data['id']

    # Sellers can't view buyer profiles
    response = client.get(f'{reverse("buyer-list")}')
    assert response.status_code == 403
    response = client.get(f'{reverse("buyer-detail", kwargs={"pk": 1})}')
    assert response.status_code == 403


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_user_creation_invalid_data(user_data, client):
    user_data['user_type'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{reverse("registration")}',
                           data=user_data,
                           format='json')
    assert response.status_code == 400


@pytest.mark.parametrize('verified_user',
                         ['DEALER'],
                         indirect=True)
def test_profile_creation_invalid_data(verified_user, dealer_profile, client):
    dealer_profile['home_country'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{reverse("dealer-creation")}',
                           data=dealer_profile,
                           format='json')
    assert response.status_code == 400


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_login_with_invalid_user_data(user_data, client):
    client.post(f'{reverse("registration")}',
                data=user_data,
                format='json')
    user_data['email'] = 'ABRA_ABRA_CADABRA'
    response = client.post(f'{reverse("get-token")}',
                           data=user_data,
                           format='json')
    assert response.status_code == 401
