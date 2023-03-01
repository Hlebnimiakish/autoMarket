import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_dealer_can_view_buyers_offers(offer, verified_user, client):
    response = client.get(reverse('offer-list'))
    assert response.status_code == 200
    assert response.data[0]['max_price']
    response = client.get(reverse('offer-detail',
                                  kwargs={'pk': 1}))
    assert response.status_code == 200
    assert response.data['car_model']


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_seller_can_not_view_buyers_offers(offer, verified_user, client):
    response = client.get(reverse('offer-list'))
    assert response.status_code == 403
    response = client.get(reverse('offer-detail',
                                  kwargs={'pk': 1}))
    assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_buyer_can_not_view_other_buyers_offers(offer, verified_user, client):
    response = client.get(reverse('offer-list'))
    assert response.status_code == 403
    response = client.get(reverse('offer-detail',
                                  kwargs={'pk': 1}))
    assert response.status_code == 403


def test_buyer_can_create_read_update_delete_his_offer(all_profiles,
                                                       offer_data,
                                                       client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    response = client.post(reverse('my-offer-list'),
                           data=offer_data)
    id = response.data['id']
    assert response.status_code == 201
    assert response.data['max_price']
    response = client.get(reverse('my-offer-list'))
    assert response.status_code == 200
    assert response.data[0]['car_model']
    response = client.get(reverse('my-offer-detail',
                                  kwargs={"pk": id}))
    assert response.status_code == 200
    assert response.data['creator']
    offer_data['max_price'] = 22222
    response = client.put(reverse('my-offer-detail',
                                  kwargs={"pk": id}),
                          data=offer_data)
    assert response.status_code == 200
    assert float(response.data['max_price']) == float(22222)
    response = client.delete(reverse('my-offer-detail',
                                     kwargs={"pk": id}))
    assert response.status_code == 200
    response = client.get(reverse('my-offer-detail',
                                  kwargs={"pk": id}))
    assert response.status_code == 404


def test_other_users_can_not_create_read_update_delete_offer(all_profiles,
                                                             offer_data,
                                                             offer,
                                                             client):
    for profile in [all_profiles['seller']['profile_instance'],
                    all_profiles['dealer']['profile_instance']]:
        client.force_authenticate(user=profile.user)
        offer_data['creator_id'] = \
            all_profiles['buyer']['profile_instance'].user.id
        response = client.post(reverse('my-offer-list'),
                               data=offer_data)
        id = offer.pk
        assert response.status_code == 403
        response = client.get(reverse('my-offer-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-offer-detail',
                                      kwargs={"pk": id}))
        assert response.status_code == 403
        offer_data['max_price'] = 22222
        response = client.put(reverse('my-offer-detail',
                                      kwargs={"pk": id}),
                              data=offer_data)
        assert response.status_code == 403
        response = client.delete(reverse('my-offer-detail',
                                         kwargs={"pk": id}))
        assert response.status_code == 403


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_offer_for_dealer_filters(offer, request, verified_user,
                                  client, all_profiles):
    client.force_authenticate(user=verified_user['user_instance'])
    new_offer = request.getfixturevalue('offer_data')
    buyer_profile = request.getfixturevalue('buyer_profile')
    client.post(reverse('buyer-creation'),
                data=buyer_profile)
    client.post(reverse('my-offer-list'),
                data=new_offer)
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    data = {'min_max_price': offer.max_price}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['max_price']) >= float(data['min_max_price'])
    data = {'max_max_price': offer.max_price}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['max_price']) <= float(data['max_max_price'])
    data = {'car_model': offer.car_model.id}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['car_model'] == data['car_model']
    data = {'creator': offer.creator.id}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['creator'] == data['creator']
    bad_data = {'min_max_price': 100000000}
    response = client.get(reverse('offer-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_offer_for_dealer_ordering_filters(offer, request, verified_user,
                                           client, all_profiles):
    client.force_authenticate(user=verified_user['user_instance'])
    new_offer = request.getfixturevalue('offer_data')
    buyer_profile = request.getfixturevalue('buyer_profile')
    client.post(reverse('buyer-creation'),
                data=buyer_profile)
    client.post(reverse('my-offer-list'),
                data=new_offer)
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    data = {'ordering': 'max_price'}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['max_price']) <= float(response.data[1]['max_price'])
    data = {'ordering': '-max_price'}
    response = client.get(reverse('offer-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['max_price']) >= float(response.data[1]['max_price'])
