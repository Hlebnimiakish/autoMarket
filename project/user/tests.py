# pylint: skip-file

import uuid
from random import choice

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from root.common.views import CustomRequest

from .models import CustomUserModel
from .views import token_link_generator

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('user_data',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_create_users_with_different_types(user_data, client):
    response = client.post(reverse("registration"),
                           data=user_data)
    assert response.status_code == 201
    assert response.data['username'] == user_data['username']
    assert response.data['user_type'] == user_data['user_type']


@pytest.mark.parametrize('unverified_user',
                         ['DEALER', 'SELLER', 'BUYER'],
                         indirect=True)
def test_user_can_read_update_delete_his_user_profile(unverified_user, client):
    response = client.get(reverse("user"))
    assert response.status_code == 200
    assert response.data['username'] == unverified_user['created_user_data']['username']
    unverified_user['created_user_data']['username'] = f'PreDelete{uuid.uuid4().hex}'
    response = client.put(reverse("user"),
                          data=unverified_user['created_user_data'])
    assert response.status_code == 200
    assert response.data['username'] == unverified_user['created_user_data']['username']
    response = client.delete(reverse("user"))
    assert response.status_code == 200
    response = client.get(reverse("user"))
    assert response.status_code == 404


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_created_user_can_log_in_and_refresh(user_data, client):
    client.post(reverse("registration"), data=user_data)
    response = client.post(reverse("get-token"),
                           data=user_data)
    refresh = response.data['refresh']
    assert response.status_code == 200
    assert response.data['access']
    response = client.post(reverse("refresh-token"),
                           data={'refresh': refresh})
    assert response.status_code == 200
    assert response.data['access']


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_inactive_user_can_not_login_and_refresh(user_data, client):
    user_data['is_active'] = False
    client.post(reverse("registration"), data=user_data)
    user_data['is_active'] = True
    response = client.post(reverse("get-token"),
                           data=user_data)
    assert response.status_code == 401


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_be_verified(unverified_user, client):
    action_type = 'verification'
    verification_link = \
        token_link_generator(unverified_user['user_instance'],
                             CustomRequest,
                             action_type,
                             action_type)
    response = client.get(verification_link)
    assert response.status_code == 200
    assert response.data['is_verified']


@pytest.mark.parametrize('unverified_user',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_not_be_verified_with_invalid_data(unverified_user,
                                                    client):
    user = unverified_user['user_instance']
    token = default_token_generator.make_token(user=user)
    verification_link = f'{reverse("verification")}?user_id=999222333&verification_token=xxx'
    response = client.get(verification_link)
    assert response.status_code == 404
    verification_link = f'{reverse("verification")}?user_id=999222333&verification_token={token}'
    response = client.get(verification_link)
    assert response.status_code == 404
    verification_link = f'{reverse("verification")}?user_id={user.pk}&verification_token=xxx'
    response = client.get(verification_link)
    assert response.status_code == 400
    verification_link = f'{reverse("verification")}?user_id={user.pk}'
    response = client.get(verification_link)
    assert response.status_code == 400
    verification_link = f'{reverse("verification")}?verification_token={token}'
    response = client.get(verification_link)
    assert response.status_code == 400


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_reset_password(user_data, client):
    client.post(reverse("registration"), data=user_data)
    email = user_data['email']
    old_password = user_data['password']
    reset_request_data = {"email": email}
    response = client.put(reverse('password-reset-request'),
                          data=reset_request_data)
    assert response.status_code == 200
    user = CustomUserModel.objects.get(email=email)
    password_reset_link = token_link_generator(user,
                                               CustomRequest,
                                               'password-reset',
                                               'password_reset')
    new_password = "testpass12345"
    password_reset_data = {"old_password": old_password,
                           "new_password": new_password}
    response = client.put(password_reset_link,
                          data=password_reset_data)
    assert response.status_code == 200
    user_data['password'] = new_password
    response = client.post(reverse("get-token"),
                           data=user_data)
    assert response.status_code == 200
    assert response.data['access']


@pytest.mark.parametrize('user_data',
                         [choice(['DEALER', 'SELLER', 'BUYER'])],
                         indirect=True)
def test_user_can_not_reset_password_with_invalid_data(user_data,
                                                       client):
    response = client.post(reverse("registration"), data=user_data)
    user = CustomUserModel.objects.get(id=response.data['id'])
    old_password = user_data['password']
    new_password = "testpass12345"
    password_reset_data = {"old_password": old_password,
                           "new_password": new_password}
    email = "nosuchmail"
    response = client.put(reverse('password-reset-request'),
                          data={"email": email})
    assert response.status_code == 404
    email = user_data['email']
    response = client.put(reverse('password-reset-request'),
                          data={"email": email})
    assert response.status_code == 200
    password_reset_link = f'{reverse("password-reset")}?user_id=999222333&' \
                          f'password_reset_token=xxx'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 404
    password_reset_link = f'{reverse("password-reset")}?user_id={user.pk}&' \
                          f'password_reset_token=xxx'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 400
    token = default_token_generator.make_token(user)
    password_reset_link = f'{reverse("password-reset")}?user_id=999222333&' \
                          f'password_reset_token={token}'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 404
    password_reset_link = f'{reverse("password-reset")}?password_reset_token={token}'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 400
    password_reset_link = f'{reverse("password-reset")}?user_id={user.pk}'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 400
    password_reset_data['new_password'] = 'i'
    password_reset_link = f'{reverse("password-reset")}?user_id={user.pk}&' \
                          f'password_reset_token={token}'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 400
    password_reset_data['new_password'] = new_password
    password_reset_data['old_password'] = 'notanoldpassword'
    password_reset_link = f'{reverse("password-reset")}?user_id={user.pk}&' \
                          f'password_reset_token={token}'
    response = client.put(password_reset_link, data=password_reset_data)
    assert response.status_code == 400


@pytest.mark.parametrize('unverified_user', ['DEALER'], indirect=True)
def test_unverified_users_can_not_create_profile(unverified_user, dealer_profile, client):
    response = client.post(reverse("dealer-creation"),
                           data=dealer_profile)
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_verified_users_can_create_profile(verified_user, dealer_profile, client):
    response = client.post(reverse("dealer-creation"),
                           data=dealer_profile)
    assert response.status_code == 201
    assert response.data['name'] == dealer_profile['name']


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
        response = client.post(reverse(f'{user_type}-creation'),
                               data=profile)
        if user_type == str.lower(verified_user['created_user_data']['user_type']):
            assert response.status_code == 201
            response = client.get(reverse(f'{user_type}-profile'))
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
    client.post(reverse(f'{user_type}-creation'),
                data=profile_data)
    response = client.get(reverse(f'{user_type}-profile'))
    assert response.status_code == 200
    assert response.data['is_active']
    profile_data = response.data
    profile_data['name'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(reverse(f'{user_type}-profile'),
                          data=profile_data)
    assert response.status_code == 200
    assert profile_data['name'] == response.data['name']
    response = client.delete(reverse(f'{user_type}-profile'))
    assert response.status_code == 200
    response = client.get(reverse(f'{user_type}-profile'))
    assert response.status_code == 404


@pytest.mark.parametrize('verified_user',
                         ['BUYER'],
                         indirect=True)
def test_buyer_can_read_update_delete_his_type_profile(verified_user,
                                                       request,
                                                       client):
    user_type = str.lower(verified_user['created_user_data']['user_type'])
    user_profile = request.getfixturevalue(f'{user_type}_profile')
    client.post(reverse("buyer-creation"),
                data=user_profile)
    response = client.get(reverse("buyer-profile"))
    assert response.status_code == 200
    assert response.data['is_active']
    profile_data = response.data
    profile_data['firstname'] = f'PreDelete{uuid.uuid4()}'
    response = client.put(reverse("buyer-profile"),
                          data=profile_data)
    assert response.status_code == 200
    assert profile_data['firstname'] == response.data['firstname']
    response = client.delete(reverse("buyer-profile"))
    assert response.status_code == 200
    response = client.get(reverse('buyer-profile'))
    assert response.status_code == 404


@pytest.mark.django_db
def test_dealer_can_view_other_users(all_users, all_profiles, client):
    dealer = all_users['dealer']
    client.force_authenticate(user=dealer['user_instance'])

    # Dealers can view all other user profiles
    for user_type in all_users.keys():
        response = client.get(reverse(f'{user_type}-list'))
        assert response.status_code == 200
        assert response.data[0]['id']
        pk = response.data[0]['id']
        response = client.get(reverse(f'{user_type}-detail',
                                      kwargs={"pk": pk}))
        assert response.status_code == 200
        assert response.data['id']


@pytest.mark.django_db
def test_buyer_can_view_other_users(all_users, all_profiles, client):
    buyer = all_users['buyer']
    client.force_authenticate(user=buyer['user_instance'])

    # Buyers can't view seller and other buyer profiles
    for user_type in ['seller', 'buyer']:
        response = client.get(reverse(f'{user_type}-list'))
        assert response.status_code == 403
        response = client.get(reverse(f'{user_type}-detail',
                                      kwargs={"pk": 1}))
        assert response.status_code == 403

    # Buyers can view dealer profiles
    response = client.get(reverse("dealer-list"))
    assert response.status_code == 200
    assert response.data[0]['id']
    pk = response.data[0]['id']
    response = client.get(reverse("dealer-detail",
                                  kwargs={"pk": pk}))
    assert response.status_code == 200
    assert response.data['id']


@pytest.mark.django_db
def test_seller_can_view_other_users(all_users, all_profiles, client):
    seller = all_users['seller']
    client.force_authenticate(user=seller['user_instance'])

    # Sellers can view dealers and other sellers profiles
    for user_type in ['seller', 'dealer']:
        response = client.get(reverse(f'{user_type}-list'))
        assert response.status_code == 200
        assert response.data[0]['id']
        pk = response.data[0]['id']
        response = client.get(reverse(f'{user_type}-detail',
                                      kwargs={"pk": pk}))
        assert response.status_code == 200
        assert response.data['id']

    # Sellers can't view buyer profiles
    response = client.get(reverse("buyer-list"))
    assert response.status_code == 403
    response = client.get(reverse("buyer-detail",
                                  kwargs={"pk": 1}))
    assert response.status_code == 403


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_user_creation_invalid_data(user_data, client):
    user_data['user_type'] = 'ABRA_ABRA_CADABRA'
    response = client.post(reverse("registration"),
                           data=user_data)
    assert response.status_code == 400


@pytest.mark.parametrize('verified_user',
                         ['DEALER'],
                         indirect=True)
def test_profile_creation_invalid_data(verified_user, dealer_profile, client):
    dealer_profile['home_country'] = 'ABRA_ABRA_CADABRA'
    response = client.post(reverse("dealer-creation"),
                           data=dealer_profile)
    assert response.status_code == 400


@pytest.mark.parametrize('user_data',
                         ['DEALER'],
                         indirect=True)
def test_login_with_invalid_user_data(user_data, client):
    client.post(reverse("registration"),
                data=user_data)
    user_data['email'] = 'ABRA_ABRA_CADABRA'
    response = client.post(reverse("get-token"),
                           data=user_data)
    assert response.status_code == 401


@pytest.mark.parametrize('verified_user',
                         ['DEALER'],
                         indirect=True)
def test_profile_search_filters(verified_user,
                                all_profiles,
                                additional_profiles,
                                client):
    data = {"search": additional_profiles['dealer']['profile_data']['name']}
    response = client.get(reverse('dealer-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['name'] == data['search']
    data = {"search": additional_profiles['seller']['profile_data']['name']}
    response = client.get(reverse('seller-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['name'] == data['search']
    for field in ['drivers_license_number', 'firstname', 'lastname']:
        data = {'search': additional_profiles['buyer']['profile_data'][str(field)]}
        response = client.get(reverse('buyer-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] == data['search']


@pytest.mark.parametrize('verified_user',
                         ['DEALER'],
                         indirect=True)
def test_dealer_profile_ordering_filters(verified_user,
                                         all_profiles,
                                         additional_profiles,
                                         client):
    data = {'ordering': 'year_of_creation'}
    response = client.get(reverse('seller-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_creation'] <= \
           response.data[1]['year_of_creation']
    data = {'ordering': '-year_of_creation'}
    response = client.get(reverse('seller-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_creation'] >= \
           response.data[1]['year_of_creation']
