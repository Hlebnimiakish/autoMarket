import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_users_can_view_dealer_auto_park(car_parks, all_users, client):
    for user in all_users.values():
        client.force_authenticate(user=user['user_instance'])
        response = client.get(reverse('dealer-park-list'))
        assert response.status_code == 200
        assert response.data[0]['available_number']
        response = client.get(reverse('dealer-park-detail',
                                      kwargs={"pk": 1}))
        assert response.status_code == 200
        assert response.data['car_price']


def test_dealer_can_view_sellers_auto_park(car_parks, client):
    user = car_parks['dealer']['park_instance'].dealer.user
    client.force_authenticate(user=user)
    response = client.get(reverse('seller-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    response = client.get(reverse('seller-park-detail',
                                  kwargs={"pk": 1}))
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
    user = car_parks['seller']['park_instance'].seller.user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-seller-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    response = client.get(reverse('my-seller-park-detail',
                                  kwargs={"pk": 1}))
    assert response.status_code == 200
    assert response.data['car_price']


def test_dealer_can_view_his_own_auto_park(car_parks, client):
    user = car_parks['dealer']['park_instance'].dealer.user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-dealer-park-list'))
    assert response.status_code == 200
    assert response.data[0]['available_number']
    response = client.get(reverse('my-dealer-park-detail',
                                  kwargs={"pk": 1}))
    assert response.status_code == 200
    assert response.data['car_price']
