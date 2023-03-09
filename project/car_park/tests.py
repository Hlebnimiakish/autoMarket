# pylint: skip-file

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_users_can_view_dealer_auto_park(car_parks, all_users, client):
    for user in all_users.values():
        client.force_authenticate(user=user['user_instance'])
        response = client.get(reverse('dealer-park-list'))
        assert response.status_code == 200
        assert response.data[0]['available_number']
        print(response.data)
        response = client.get(reverse('dealer-park-detail',
                                      kwargs={"pk": 1}))
        assert response.status_code == 200
        assert response.data['car_price']


def test_dealer_can_view_sellers_auto_park(car_parks, client):
    user = car_parks['dealer_park'].dealer.user
    client.force_authenticate(user=user)
    response = client.get(reverse('seller-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    pk = response.data[0]['id']
    response = client.get(reverse('seller-park-detail',
                                  kwargs={"pk": pk}))
    assert response.status_code == 200
    assert response.data['car_price']


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_buyer_can_not_view_sellers_auto_park(verified_user, car_parks, client):
    response = client.get(reverse('seller-park-list'))
    assert response.status_code == 403
    response = client.get(reverse('seller-park-detail',
                                  kwargs={"pk": 1}))
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_seller_can_not_view_other_sellers_auto_park(verified_user, car_parks, client):
    response = client.get(reverse('seller-park-list'))
    assert response.status_code == 403
    response = client.get(reverse('seller-park-detail',
                                  kwargs={"pk": 1}))
    assert response.status_code == 403


def test_seller_can_view_his_own_auto_park(car_parks, client):
    user = car_parks['seller_park'].seller.user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-seller-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    pk = response.data[0]['id']
    response = client.get(reverse('my-seller-park-detail',
                                  kwargs={"pk": pk}))
    assert response.status_code == 200
    assert response.data['car_price']


def test_dealer_can_view_his_own_auto_park(car_parks, client):
    user = car_parks['dealer_park'].dealer.user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-dealer-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    pk = response.data[0]['id']
    response = client.get(reverse('my-dealer-park-detail',
                                  kwargs={"pk": pk}))
    assert response.status_code == 200
    assert response.data['car_price']


@pytest.mark.parametrize('user_park', ['dealer'], indirect=True)
def test_dealer_front_park_filters(car_parks, all_profiles, user_park, client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    param_field = {'dealer': 'dealer',
                   'car_model': 'car_model'}
    for param, field in param_field.items():
        data = {str(param): user_park['park_data'][str(field)]}
        response = client.get(reverse('dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] == \
               data[str(param)]
    param_field = {'min_available_number': 'available_number',
                   'min_car_price': 'car_price'}
    for param, field in param_field.items():
        data = {str(param): user_park['park_data'][str(field)]}
        response = client.get(reverse('dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] >= \
               data[str(param)]
    data = {'max_car_price': user_park['park_data']['car_price']}
    response = client.get(reverse('dealer-park-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['car_price'] <= \
           data['max_car_price']
    bad_data = {'min_car_price': 100000000}
    response = client.get(reverse('dealer-park-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('user_park', ['seller'], indirect=True)
def test_seller_front_park_filters(car_parks, all_profiles, user_park, client):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    param_field = {'seller': 'seller',
                   'car_model': 'car_model'}
    for param, field in param_field.items():
        data = {str(param): user_park['park_data'][str(field)]}
        response = client.get(reverse('seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] == \
               data[str(param)]
    param_field = {'min_available_number': 'available_number',
                   'min_car_price': 'car_price'}
    for param, field in param_field.items():
        data = {str(param): user_park['park_data'][str(field)]}
        response = client.get(reverse('seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] >= \
               data[str(param)]
    data = {'max_car_price': user_park['park_data']['car_price']}
    response = client.get(reverse('seller-park-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['car_price'] <= \
           data['max_car_price']
    bad_data = {'min_car_price': 100000000}
    response = client.get(reverse('seller-park-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('car_park', ['dealer'], indirect=True)
def test_dealer_own_park_filters(car_parks, car_park, client):
    user = car_park['park_instance'].dealer.user
    client.force_authenticate(user=user)
    param_field = {'dealer': 'dealer',
                   'car_model': 'car_model'}
    for param, field in param_field.items():
        data = {str(param): car_park['park_data'][str(field)]}
        response = client.get(reverse('my-dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] == \
               data[str(param)]
    param_field = {'min_available_number': 'available_number',
                   'min_car_price': 'car_price'}
    for param, field in param_field.items():
        data = {str(param): car_park['park_data'][str(field)]}
        response = client.get(reverse('my-dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] >= \
               data[str(param)]
    data = {'max_car_price': car_park['park_data']['car_price']}
    response = client.get(reverse('my-dealer-park-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['car_price'] <= \
           data['max_car_price']
    bad_data = {'min_car_price': 100000000}
    response = client.get(reverse('my-dealer-park-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('car_park', ['seller'], indirect=True)
def test_seller_own_park_filters(car_parks, car_park, client):
    user = car_park['park_instance'].seller.user
    client.force_authenticate(user=user)
    param_field = {'seller': 'seller',
                   'car_model': 'car_model'}
    for param, field in param_field.items():
        data = {str(param): car_park['park_data'][str(field)]}
        response = client.get(reverse('my-seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] == \
               data[str(param)]
    param_field = {'min_available_number': 'available_number',
                   'min_car_price': 'car_price'}
    for param, field in param_field.items():
        data = {str(param): car_park['park_data'][str(field)]}
        response = client.get(reverse('my-seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] >= \
               data[str(param)]
    data = {'max_car_price': car_park['park_data']['car_price']}
    response = client.get(reverse('my-seller-park-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['car_price'] <= \
           data['max_car_price']
    bad_data = {'min_car_price': 100000000}
    response = client.get(reverse('my-seller-park-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('user_park', ['dealer'], indirect=True)
def test_dealer_front_park_ordering_filters(car_parks, all_profiles, user_park, client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    for field in ['available_number', 'car_price']:
        data = {'ordering': field}
        response = client.get(reverse('dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) <= float(response.data[1][field])
        data = {'ordering': f'-{field}'}
        response = client.get(reverse('dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) >= float(response.data[1][field])


@pytest.mark.parametrize('user_park', ['seller'], indirect=True)
def test_seller_front_park_ordering_filters(car_parks, all_profiles, user_park, client):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    for field in ['available_number', 'car_price']:
        data = {'ordering': field}
        response = client.get(reverse('seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) <= float(response.data[1][field])
        data = {'ordering': f'-{field}'}
        response = client.get(reverse('seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) >= float(response.data[1][field])


@pytest.mark.parametrize('car_park', ['dealer'], indirect=True)
def test_dealer_own_park_ordering_filters(car_parks, all_profiles, car_park, client):
    user = car_park['park_instance'].dealer.user
    client.force_authenticate(user=user)
    for field in ['available_number', 'car_price']:
        data = {'ordering': field}
        response = client.get(reverse('my-dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) <= float(response.data[1][field])
        data = {'ordering': f'-{field}'}
        response = client.get(reverse('my-dealer-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) >= float(response.data[1][field])


@pytest.mark.parametrize('car_park', ['seller'], indirect=True)
def test_seller_own_park_ordering_filters(car_parks, all_profiles, car_park, client):
    user = car_park['park_instance'].seller.user
    client.force_authenticate(user=user)
    for field in ['available_number', 'car_price']:
        data = {'ordering': field}
        response = client.get(reverse('my-seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) <= float(response.data[1][field])
        data = {'ordering': f'-{field}'}
        response = client.get(reverse('my-seller-park-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][field]) >= float(response.data[1][field])
