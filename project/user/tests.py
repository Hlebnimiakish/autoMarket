import uuid
from random import randint

import requests

ENDPOINT = 'http://127.0.0.1:8000/users/'


def create_user_data(name: str, user_type: str):
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"{name}{filler}",
        "password": f"pass{password}",
        "email": f"{name}{filler}@am.com",
        "user_type": f"{user_type}"
    }
    return user_data


def create_different_verified_users():
    dealer_data = create_user_data("dealer", "DEALER")
    seller_data = create_user_data("seller", "SELLER")
    buyer_data = create_user_data("buyer", "BUYER")
    user_data = {'dealer': dealer_data, 'seller': seller_data, 'buyer': buyer_data}
    for u in user_data.values():
        cr_u = create_custom_user(u)
        verify_user(cr_u.json()['id'])
    return user_data


def create_dealer_profile_data():
    dealer_profile_data = {
        "name": f"tdealer{uuid.uuid4().hex}",
        "home_country": "AL"
    }
    return dealer_profile_data


def create_seller_profile_data():
    seller_profile_data = {
        "name": f"tseller{uuid.uuid4().hex}",
        "year_of_creation": randint(1000, 2023)
    }
    return seller_profile_data


def create_buyer_profile_data():
    buyer_profile_data = {
        "firstname": f"tbuyer{uuid.uuid4().hex}",
        "lastname": f"tbuyer{uuid.uuid4().hex}",
        "drivers_license_number": str(uuid.uuid4().hex)
    }
    return buyer_profile_data


def my_key_header(key: str):
    headers = {
        'Authorization': f'Bearer {str(key)}'
    }
    return headers


def auth_view_some_url(suffix: str, headers: dict, id: str = ''):
    return requests.get(ENDPOINT + str(suffix) + str(id),
                        headers=headers)


def create_custom_user(data: dict):
    return requests.post(ENDPOINT + 'registration/', json=data)


def verify_user(user_id: int):
    id_data = {'user_id': user_id}
    return requests.put(ENDPOINT + 'verification/', json=id_data)


def get_my_profile(profile_type: str, key: str):
    headers = my_key_header(key)
    return requests.get(ENDPOINT + f'my_{profile_type}_profile/',
                        headers=headers)


def change_my_profile(data: dict, profile_type: str, key: str):
    headers = my_key_header(key)
    return requests.put(ENDPOINT + f'my_{profile_type}_profile/',
                        headers=headers,
                        json=data)


def delete_my_profile(profile_type: str, key: str):
    headers = my_key_header(key)
    return requests.delete(ENDPOINT + f'my_{profile_type}_profile/',
                           headers=headers)


def create_user_profile(data: dict, user_type: str, key: str):
    headers = my_key_header(key)
    return requests.post(ENDPOINT + f'create_{user_type}_profile/',
                         json=data,
                         headers=headers)


def user_login(data: dict):
    return requests.post(ENDPOINT + 'login/', json=data)


def get_key(data: dict):
    login_request = requests.post(ENDPOINT + 'login/', json=data)
    return login_request.json()['access']


def test_create_users_with_different_types():
    dealer = create_user_data("dealer", "DEALER")
    seller = create_user_data("seller", "SELLER")
    buyer = create_user_data("buyer", "BUYER")
    u_list = [dealer, seller, buyer]
    for u in u_list:
        u_creation_response = create_custom_user(data=u)
        assert u_creation_response.status_code == 201
        assert u_creation_response.json()['username'] == u['username']
        assert u_creation_response.json()['user_type'] == u['user_type']


def test_user_can_read_update_delete_his_profile():
    user_data = create_user_data('RUDtest', 'BUYER')
    new_user = create_custom_user(user_data)
    key = get_key(user_data)
    headers = my_key_header(key)
    view_user = requests.get(ENDPOINT + 'my_user_page/',
                             headers=headers)
    assert view_user.status_code == 200
    assert view_user.json()['username'] == new_user.json()['username']
    user_data['username'] = f'PreDelete{uuid.uuid4().hex}'
    update_user = requests.put(ENDPOINT + 'my_user_page/',
                               headers=headers,
                               json=user_data)
    assert update_user.status_code == 200
    assert update_user.json()['username'] == user_data['username']
    delete_user = requests.delete(ENDPOINT + 'my_user_page/',
                                  headers=headers)
    assert delete_user.status_code == 200


def test_created_user_can_log_in_and_refresh():
    user_data = create_user_data("login", "DEALER")
    create_custom_user(user_data)
    login_response = user_login(user_data)
    assert 'access' in login_response.json()
    refresh = login_response.json()['refresh']
    print(refresh)
    refr_request = requests.post(ENDPOINT + 'login/refresh_token/',
                                 json={'refresh': refresh})
    print(refr_request)
    assert refr_request.status_code == 200
    assert 'access' in refr_request.json()


def test_user_can_be_verified():
    dealer = create_user_data("dealer", "DEALER")
    created_user = create_custom_user(data=dealer)
    verify = verify_user(created_user.json()['id'])
    assert verify.status_code == 200
    assert verify.json()['is_verified']


def test_unverified_users_can_not_create_profile_and_verified_can():
    dealer = create_user_data('name', 'DEALER')
    created_user = create_custom_user(dealer)
    key = get_key(dealer)
    dealer_profile_data = create_dealer_profile_data()
    assert create_user_profile(dealer_profile_data,
                               'dealer',
                               key).status_code == 403
    verify_user(created_user.json()['id'])
    assert create_user_profile(dealer_profile_data,
                               'dealer',
                               key).status_code == 201


def test_users_with_different_types_can_create_only_corresponding_profile():
    user_data = create_different_verified_users()

    key = get_key(user_data['dealer'])
    dealer_profile_data = create_dealer_profile_data()
    assert create_user_profile(dealer_profile_data,
                               'seller',
                               key).status_code == 403
    assert create_user_profile(dealer_profile_data,
                               'dealer',
                               key).status_code == 201
    assert get_my_profile('dealer', key).status_code == 200

    key = get_key(user_data['seller'])
    seller_profile_data = create_seller_profile_data()
    assert create_user_profile(seller_profile_data,
                               'dealer',
                               key).status_code == 403
    assert create_user_profile(seller_profile_data,
                               'seller',
                               key).status_code == 201
    assert get_my_profile('seller', key).status_code == 200

    key = get_key(user_data['buyer'])
    buyer_profile_data = create_buyer_profile_data()
    assert create_user_profile(buyer_profile_data,
                               'seller',
                               key).status_code == 403
    assert create_user_profile(buyer_profile_data,
                               'buyer',
                               key).status_code == 201
    assert get_my_profile('buyer', key).status_code == 200


def test_user_can_read_update_delete_his_created_profile():
    user_data = create_different_verified_users()

    u_type = 'dealer'
    key = get_key(user_data[u_type])
    dealer_profile_data = create_dealer_profile_data()
    create_user_profile(dealer_profile_data,
                        u_type,
                        key)
    my_profile = get_my_profile(u_type, key)
    assert my_profile.status_code == 200
    profile_data = my_profile.json()
    profile_data['name'] = 'PreDelete'
    profile_upd = change_my_profile(profile_data,
                                    u_type,
                                    key)
    assert profile_upd.status_code == 200
    assert profile_upd.json()['name'] == 'PreDelete'
    assert delete_my_profile(u_type, key).status_code == 200
    assert get_my_profile(u_type, key).status_code == 404

    u_type = 'seller'
    key = get_key(user_data[u_type])
    seller_profile_data = create_seller_profile_data()
    create_user_profile(seller_profile_data,
                        u_type,
                        key)
    my_profile = get_my_profile(u_type, key)
    assert my_profile.status_code == 200
    profile_data = my_profile.json()
    profile_data['name'] = 'PreDelete'
    profile_upd = change_my_profile(profile_data,
                                    u_type,
                                    key)
    assert profile_upd.status_code == 200
    assert profile_upd.json()['name'] == 'PreDelete'
    assert delete_my_profile(u_type, key).status_code == 200
    assert get_my_profile(u_type, key).status_code == 404

    u_type = 'buyer'
    key = get_key(user_data[u_type])
    buyer_profile_data = create_buyer_profile_data()
    create_user_profile(buyer_profile_data,
                        u_type,
                        key)
    my_profile = get_my_profile(u_type, key)
    assert my_profile.status_code == 200
    profile_data = my_profile.json()
    profile_data['firstname'] = 'PreDelete'
    profile_upd = change_my_profile(profile_data,
                                    u_type,
                                    key)
    assert profile_upd.status_code == 200
    assert profile_upd.json()['firstname'] == 'PreDelete'
    assert delete_my_profile(u_type, key).status_code == 200
    assert get_my_profile(u_type, key).status_code == 404


def test_users_can_view_other_users_data():
    user_data = create_different_verified_users()

    u_type = 'dealer'
    key_dealer = get_key(user_data[u_type])
    headers_dealer = my_key_header(key_dealer)
    dealer_profile_data = create_dealer_profile_data()
    create_user_profile(dealer_profile_data,
                        u_type,
                        key_dealer)

    u_type = 'seller'
    key_seller = get_key(user_data[u_type])
    headers_seller = my_key_header(key_seller)
    seller_profile_data = create_seller_profile_data()
    create_user_profile(seller_profile_data,
                        u_type,
                        key_seller)

    u_type = 'buyer'
    key_buyer = get_key(user_data[u_type])
    headers_buyer = my_key_header(key_buyer)
    buyer_profile_data = create_buyer_profile_data()
    create_user_profile(buyer_profile_data,
                        u_type,
                        key_buyer)

    # Dealers can view all other user profiles
    for user_type in ['dealers/', 'buyers/', 'sellers/']:
        view_plural = auth_view_some_url(suffix=user_type,
                                         headers=headers_dealer)
        assert view_plural.status_code == 200
        assert 'id' in view_plural.json()[0]
        view_singular = auth_view_some_url(suffix=user_type,
                                           headers=headers_dealer,
                                           id=f"{view_plural.json()[0]['id']}/")
        assert view_singular.status_code == 200
        assert 'id' in view_singular.json()

    # Sellers can view dealers and other sellers profiles
    for user_type in ['dealers/', 'sellers/']:
        view_plural = auth_view_some_url(suffix=user_type,
                                         headers=headers_seller)
        assert view_plural.status_code == 200
        assert 'id' in view_plural.json()[0]
        view_singular = auth_view_some_url(suffix=user_type,
                                           headers=headers_seller,
                                           id=f"{view_plural.json()[0]['id']}/")
        assert view_singular.status_code == 200
        assert 'id' in view_singular.json()

    # Sellers can't view buyers profiles
    view_plural = auth_view_some_url(suffix='buyers/',
                                     headers=headers_seller)
    assert view_plural.status_code == 403
    view_singular = auth_view_some_url(suffix='buyers/',
                                       headers=headers_seller,
                                       id='1/')
    assert view_singular.status_code == 403

    # Buyers can't view sellers and other buyers profiles
    for user_type in ['sellers/', 'buyers/']:
        view_plural = auth_view_some_url(suffix=user_type,
                                         headers=headers_buyer)
        assert view_plural.status_code == 403
        view_singular = auth_view_some_url(suffix=user_type,
                                           headers=headers_buyer,
                                           id='1/')
        assert view_singular.status_code == 403

    # Buyers can view dealers profiles
    view_plural = auth_view_some_url(suffix='dealers/',
                                     headers=headers_buyer)
    assert view_plural.status_code == 200
    assert 'id' in view_plural.json()[0]
    view_singular = auth_view_some_url(suffix='dealers/',
                                       headers=headers_buyer,
                                       id='1/')
    assert view_singular.status_code == 200
    assert 'id' in view_singular.json()


def test_invalid_data_tests():
    incorrect_user_data = create_user_data('incorrect', 'ABRA CADABRA')
    creation = create_custom_user(incorrect_user_data)
    assert creation.status_code == 400
    correct_user_data = create_user_data('correct', 'DEALER')
    created_user = create_custom_user(correct_user_data)
    verify_user(created_user.json()['id'])
    key = get_key(correct_user_data)
    to_incorrect_dealer_profile = create_dealer_profile_data()
    to_incorrect_dealer_profile['home_country'] = 'ABRACADABRA'
    creation = create_user_profile(to_incorrect_dealer_profile, 'dealer', key)
    assert creation.status_code == 400
    correct_user_data['email'] = 'abra'
    login = user_login(correct_user_data)
    assert login.status_code == 401
