import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_all_users_can_view_dealer_promos(all_users,
                                          dealer_promo,
                                          client):
    for user in all_users.values():
        client.force_authenticate(user['user_instance'])
        response = client.get(reverse('dealer-promo-list'))
        assert response.status_code == 200
        assert response.data[0]['discount_size']
        response = client.get(reverse('dealer-promo-detail',
                                      kwargs={'pk': 1}))
        assert response.status_code == 200
        assert response.data['promo_cars']


def test_dealers_and_sellers_can_view_seller_promos(all_users,
                                                    seller_promo,
                                                    client):
    for user in [all_users['dealer'], all_users['seller']]:
        client.force_authenticate(user['user_instance'])
        response = client.get(reverse('seller-promo-list'))
        assert response.status_code == 200
        assert response.data[0]['discount_size']
        response = client.get(reverse('seller-promo-detail',
                                      kwargs={'pk': 1}))
        assert response.status_code == 200
        assert response.data['promo_cars']


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_buyers_can_not_view_seller_promos(verified_user,
                                           seller_promo,
                                           client):
    response = client.get(reverse('seller-promo-list'))
    assert response.status_code == 403
    response = client.get(reverse('seller-promo-detail',
                                  kwargs={'pk': 1}))
    assert response.status_code == 403


def test_dealer_and_seller_can_create_read_update_delete_his_promo(all_profiles,
                                                                   promo_data,
                                                                   car_parks,
                                                                   client):
    for user_type, aim in {'dealer': 'buyer',
                           'seller': 'dealer'}.items():
        client.force_authenticate(all_profiles[str(user_type)]['profile_instance'].user)
        promo_data['creator'] = all_profiles[str(user_type)]['profile_instance'].pk
        promo_data['promo_cars'] = [car_parks[f'{user_type}_park'].pk]
        promo_data['promo_aims'] = [all_profiles[str(aim)]['profile_instance'].pk]
        response = client.post(reverse(f'my-{user_type}-promo-list'),
                               data=promo_data)
        assert response.status_code == 201
        assert response.data['discount_size']
        id = response.data['id']
        response = client.get(reverse(f'my-{user_type}-promo-list'))
        assert response.status_code == 200
        assert response.data[0]['creator']
        response = client.get(reverse(f'my-{user_type}-promo-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 200
        assert response.data['creator']
        promo_data['discount_size'] = 90
        response = client.put(reverse(f'my-{user_type}-promo-detail',
                                      kwargs={'pk': id}),
                              data=promo_data)
        assert response.status_code == 200
        assert float(response.data['discount_size']) == float(90)
        response = client.delete(reverse(f'my-{user_type}-promo-detail',
                                         kwargs={'pk': id}))
        assert response.status_code == 200
        response = client.get(reverse(f'my-{user_type}-promo-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 404


def test_seller_and_buyer_can_not_create_read_update_delete_dealer_promo(all_profiles,
                                                                         promo_data,
                                                                         dealer_promo,
                                                                         car_parks,
                                                                         client):
    for user_type, aim in {'seller': 'buyer',
                           'buyer': 'seller'}.items():
        client.force_authenticate(all_profiles[str(user_type)]['profile_instance'].user)
        promo_data['creator'] = all_profiles[str(user_type)]['profile_instance'].pk
        promo_data['promo_cars'] = [car_parks['dealer_park'].pk]
        promo_data['promo_aims'] = [all_profiles[str(aim)]['profile_instance'].pk]
        response = client.post(reverse('my-dealer-promo-list'),
                               data=promo_data)
        assert response.status_code == 403
        id = dealer_promo['promo'].pk
        promo_data = dealer_promo['promo_data']
        response = client.get(reverse('my-dealer-promo-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-dealer-promo-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 403
        promo_data['discount_size'] = 90
        response = client.put(reverse('my-dealer-promo-detail',
                                      kwargs={'pk': id}),
                              data=promo_data)
        assert response.status_code == 403
        response = client.delete(reverse('my-dealer-promo-detail',
                                         kwargs={'pk': id}))
        assert response.status_code == 403


def test_dealer_and_buyer_can_not_create_read_update_delete_seller_promo(all_profiles,
                                                                         promo_data,
                                                                         seller_promo,
                                                                         car_parks,
                                                                         client):
    for user_type, aim in {'dealer': 'buyer',
                           'buyer': 'dealer'}.items():
        client.force_authenticate(all_profiles[str(user_type)]['profile_instance'].user)
        promo_data['creator'] = all_profiles[str(user_type)]['profile_instance'].pk
        promo_data['promo_cars'] = [car_parks['seller_park'].pk]
        promo_data['promo_aims'] = [all_profiles[str(aim)]['profile_instance'].pk]
        response = client.post(reverse('my-seller-promo-list'),
                               data=promo_data)
        assert response.status_code == 403
        id = seller_promo['promo'].pk
        promo_data = seller_promo['promo_data']
        response = client.get(reverse('my-seller-promo-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-seller-promo-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 403
        promo_data['discount_size'] = 90
        response = client.put(reverse('my-seller-promo-detail',
                                      kwargs={'pk': id}),
                              data=promo_data)
        assert response.status_code == 403
        response = client.delete(reverse('my-seller-promo-detail',
                                         kwargs={'pk': id}))
        assert response.status_code == 403


@pytest.mark.parametrize('additional_promo', ['dealer', 'seller'], indirect=True)
def test_promo_front_filters(seller_promo, dealer_promo, car_parks,
                             client, additional_promo, all_profiles):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    user_type = str(additional_promo['promo_instance'].creator.user.user_type).lower()
    promos = {'dealer': dealer_promo, 'seller': seller_promo}
    for f in ['promo_name', 'promo_description', 'creator']:
        data = {str(f): promos[str(user_type)]['promo_data'][str(f)]}
        response = client.get(reverse(f'{str(user_type)}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(f)] == data[str(f)]
    for f in ['end_date', 'discount_size']:
        data = {str(f): promos[str(user_type)]['promo_data'][str(f)]}
        response = client.get(reverse(f'{str(user_type)}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(f)] >= data[str(f)]
    data = {'start_after_date': promos[str(user_type)]['promo_data']['start_date']}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['start_date'] >= data['start_after_date']
    data = {'start_before_date': promos[str(user_type)]['promo_data']['start_date']}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['start_date'] <= data['start_before_date']
    for f in ['promo_aims', 'promo_cars']:
        data = {str(f): promos[str(user_type)]['promo_data'][str(f)][0]}
        response = client.get(reverse(f'{str(user_type)}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert data[str(f)] in response.data[0][str(f)]
    bad_data = {'discount_size': 15000}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=bad_data)
    assert response.data == []


@pytest.mark.parametrize('additional_promo', ['dealer', 'seller'], indirect=True)
def test_promo_own_filters(client, dealer_promo,
                           seller_promo, additional_promo):
    user = additional_promo['promo_instance'].creator.user
    client.force_authenticate(user=user)
    user_type = str(user.user_type).lower()
    for f in ['promo_name', 'promo_description', 'creator']:
        data = {str(f): additional_promo['promo_data'][str(f)]}
        response = client.get(reverse(f'my-{user_type}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(f)] == data[str(f)]
    for f in ['end_date', 'discount_size']:
        data = {str(f): additional_promo['promo_data'][str(f)]}
        response = client.get(reverse(f'my-{user_type}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(f)] >= data[str(f)]
    data = {'start_after_date': additional_promo['promo_data']['start_date']}
    response = client.get(reverse(f'my-{user_type}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['start_date'] >= data['start_after_date']
    data = {'start_before_date': additional_promo['promo_data']['start_date']}
    response = client.get(reverse(f'my-{user_type}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['start_date'] <= data['start_before_date']
    for f in ['promo_aims', 'promo_cars']:
        data = {str(f): additional_promo['promo_data'][str(f)][0]}
        response = client.get(reverse(f'my-{user_type}-promo-list'),
                              data=data)
        assert response.status_code == 200
        assert data[str(f)] in response.data[0][str(f)]
    bad_data = {'discount_size': 150000}
    response = client.get(reverse(f'my-{user_type}-promo-list'),
                          data=bad_data)
    assert response.data == []


@pytest.mark.parametrize('additional_promo', ['dealer', 'seller'], indirect=True)
def test_promo_front_ordering_filters(seller_promo, dealer_promo, client,
                                      additional_promo, all_profiles):
    user = all_profiles['dealer']['profile_instance'].user
    client.force_authenticate(user=user)
    user_type = str(additional_promo['promo_instance'].creator.user.user_type).lower()
    data = {'ordering': 'discount_size'}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['discount_size']) <= \
           float(response.data[1]['discount_size'])
    data = {'ordering': '-discount_size'}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['discount_size']) >= \
           float(response.data[1]['discount_size'])


@pytest.mark.parametrize('additional_promo', ['dealer', 'seller'], indirect=True)
def test_promo_own_ordering_filters(seller_promo, dealer_promo, client,
                                    additional_promo):
    user = additional_promo['promo_instance'].creator.user
    client.force_authenticate(user=user)
    user_type = str(user.user_type).lower()
    data = {'ordering': 'discount_size'}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['discount_size']) <= \
           float(response.data[1]['discount_size'])
    data = {'ordering': '-discount_size'}
    response = client.get(reverse(f'{str(user_type)}-promo-list'),
                          data=data)
    assert response.status_code == 200
    assert float(response.data[0]['discount_size']) >= \
           float(response.data[1]['discount_size'])
