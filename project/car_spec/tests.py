# pylint: skip-file

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_dealer_can_create_spec(verified_user, spec_data, client, dealer_profile):
    response = client.post(reverse("dealer-creation"),
                           data=dealer_profile)
    spec_data['dealer'] = response.data
    response = client.post(reverse('create-spec'),
                           data=spec_data)
    assert response.status_code == 201
    assert response.data['min_year_of_production']


def test_other_users_can_not_create_spec(all_profiles, spec_data, client):
    for profile in [all_profiles['seller']['profile_instance'],
                    all_profiles['buyer']['profile_instance']]:
        client.force_authenticate(user=profile.user)
        response = client.post(reverse('create-spec'),
                               data=spec_data)
        assert response.status_code == 403


def test_dealer_can_not_create_second_spec(spec, spec_data, client):
    user = spec['spec_instance'].dealer.user
    client.force_authenticate(user=user)
    spec_data['dealer'] = spec['spec_data']['dealer']
    response = client.post(reverse('create-spec'),
                           data=spec_data)
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_seller_can_view_dealers_spec(verified_user, spec, client):
    user = verified_user['user_instance']
    client.force_authenticate(user=user)
    response = client.get(reverse('dealer-specs'))
    assert response.status_code == 200
    assert response.data[0]['transmission']


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_buyer_can_not_view_dealers_spec(verified_user, spec, client):
    user = verified_user['user_instance']
    client.force_authenticate(user=user)
    response = client.get(reverse('dealer-specs'))
    assert response.status_code == 403


def test_dealer_can_read_update_delete_his_spec(spec, client):
    user = spec['spec_instance'].dealer.user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-spec'))
    assert response.status_code == 200
    assert response.data['color']
    spec['spec_data']['color'] = 'green'
    response = client.put(reverse('my-spec'),
                          data=spec['spec_data'])
    assert response.status_code == 200
    assert response.data['color'] == 'green'
    response = client.delete(reverse('my-spec'))
    assert response.status_code == 200
    response = client.get(reverse('my-spec'))
    assert response.status_code == 404


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_seller_can_view_dealers_suitable_cars(suit_cars, verified_user, client):
    response = client.get(reverse('suitable-car-list'))
    assert response.status_code == 200
    assert response.data[0]['car_model']
    pk = response.data[0]['id']
    response = client.get(reverse('suitable-car-detail',
                                  kwargs={'pk': pk}))
    assert response.status_code == 200
    assert response.data['car_model']


def test_dealer_can_view_his_suitable_cars(suit_cars, client):
    user = suit_cars['dealer'].user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-suitable-car-list'))
    assert response.status_code == 200
    assert response.data[0]['car_model']
    pk = response.data[0]['id']
    response = client.get(reverse('my-suitable-car-detail',
                                  kwargs={'pk': pk}))
    assert response.status_code == 200
    assert response.data['car_model']


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_buyer_can_not_view_dealer_suitable_cars(suit_cars, verified_user, client):
    response = client.get(reverse('suitable-car-list'))
    assert response.status_code == 403
    response = client.get(reverse('suitable-car-detail',
                                  kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_front_suitable_cars_filters(suit_cars, verified_user, client):
    user = verified_user['user_instance']
    client.force_authenticate(user=user)
    car_model_id = suit_cars['cars'][3].pk
    data = {'car_model': car_model_id}
    response = client.get(reverse('suitable-car-list'),
                          data=data)
    assert response.status_code == 200
    assert data['car_model'] in response.data[0]['car_model']
    dealer_id = suit_cars['dealer'].pk
    data = {'dealer': dealer_id}
    response = client.get(reverse('suitable-car-list'),
                          data=data)
    assert response.status_code == 200
    assert data['dealer'] == response.data[0]['dealer']


def test_own_suitable_cars_filter(suit_cars, client):
    user = suit_cars['dealer'].user
    client.force_authenticate(user=user)
    car_model_id = suit_cars['cars'][2].pk
    data = {'car_model': car_model_id}
    response = client.get(reverse('my-suitable-car-list'),
                          data=data)
    assert response.status_code == 200
    assert data['car_model'] in response.data[0]['car_model']
