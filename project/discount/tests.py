# pylint: skip-file

from random import randint

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_dealer_can_view_seller_discounts(all_profiles,
                                          additional_profiles,
                                          discounts,
                                          client):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    response = client.get(reverse('sellers-discounts-list'))
    assert response.status_code == 200
    assert response.data[0]['purchase_number_discount_map']
    pk = response.data[0]['id']
    response = client.get(reverse('sellers-discounts-detail',
                                  kwargs={'pk': pk}))
    assert response.status_code == 200
    assert response.data['purchase_number_discount_map']


def test_dealer_can_view_his_discount_level(all_profiles,
                                            current_levels,
                                            client):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-current-dealer-discounts-list'))
    assert response.status_code == 200
    assert response.data[0]['current_discount']
    pk = response.data[0]['id']
    response = client.get(reverse('my-current-dealer-discounts-detail',
                                  kwargs={'pk': pk}))
    assert response.status_code == 200
    assert response.data['current_purchase_number']


def test_seller_can_view_his_current_discounts(all_profiles,
                                               current_levels,
                                               client):
    user = all_profiles['seller']['profile_instance'].user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-current-seller-discounts-list'))
    assert response.status_code == 200
    assert response.data[0]['current_discount']
    pk = response.data[0]['id']
    response = client.get(reverse('my-current-seller-discounts-detail',
                                  kwargs={'pk': pk}))
    assert response.status_code == 200
    assert response.data['current_purchase_number']


def test_seller_can_create_his_discount_levels_with_correct_data(all_profiles,
                                                                 client):
    user = all_profiles['seller']['profile_instance'].user
    client.force_authenticate(user=user)
    discount_map = {randint(1, 2): randint(3, 10),
                    randint(5, 10): randint(11, 15),
                    randint(20, 50): randint(20, 30)}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 201
    assert response.data['purchase_number_discount_map']


def test_seller_can_not_create_discount_levels_second_time(all_profiles,
                                                           discounts,
                                                           client):
    user = all_profiles['seller']['profile_instance'].user
    client.force_authenticate(user=user)
    discount_map = {randint(1, 2): randint(3, 10),
                    randint(5, 10): randint(11, 15),
                    randint(20, 50): randint(20, 30)}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 403


def test_seller_can_not_create_discount_levels_with_incorrect_data(all_profiles,
                                                                   client):
    user = all_profiles['seller']['profile_instance'].user
    client.force_authenticate(user=user)
    discount_map = "abra"
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 400
    discount_map = {"abra"}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 400
    discount_map = {"abra": "cadabra"}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 400
    discount_map = {"abra": 1}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 400
    discount_map = {"500": 101}
    response = client.post(reverse("create-discount-levels"),
                           data={'purchase_number_discount_map': discount_map})
    assert response.status_code == 400


def test_seller_can_read_update_delete_his_discount_levels(all_profiles,
                                                           discounts,
                                                           client):
    user = all_profiles['seller']['profile_instance'].user
    client.force_authenticate(user=user)
    response = client.get(reverse('my-discount-levels'))
    assert response.status_code == 200
    assert response.data['purchase_number_discount_map']
    data = response.data
    key_list = [key for key in data['purchase_number_discount_map'].keys()]
    data['purchase_number_discount_map'][key_list[0]] = 99
    response = client.put(reverse('my-discount-levels'),
                          data=data)
    assert response.status_code == 200
    assert 99 in response.data['purchase_number_discount_map'].values()
    response = client.delete(reverse('my-discount-levels'))
    assert response.status_code
    response = client.get(reverse('my-discount-levels'))
    assert response.status_code == 404


def test_sellers_discount_levels_search_filter(all_profiles,
                                               additional_profiles,
                                               discounts,
                                               client):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    name = additional_profiles['seller']['profile_instance'].name
    data = {"search": name}
    response = client.get(reverse('sellers-discounts-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['purchase_number_discount_map']
