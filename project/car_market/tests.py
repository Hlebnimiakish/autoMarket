import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_users_can_view_cars_on_market(client, all_users, cars):
    for user in all_users.values():
        client.force_authenticate(user=user['user_instance'])
        response = client.get(reverse('car-list'))
        assert response.status_code == 200
        assert response.data[0]['brand_name']
        response = client.get(reverse('car-detail', kwargs={"pk": 1}))
        assert response.status_code == 200
        assert response.data['car_model_name']


@pytest.mark.parametrize('verified_user', ['BUYER'], indirect=True)
def test_market_filters(client, verified_user, cars):
    client.force_authenticate(user=verified_user['user_instance'])
    response = client.get(reverse('car-list'))
    test_instance = response.data[3]
    for param in ['engine_volume', 'drive_unit', 'engine_fuel_type',
                  'transmission', 'body_type', 'safe_controls',
                  'parking_help', 'climate_controls', 'multimedia',
                  'additional_safety', 'other_additions']:
        data = {str(param): test_instance[str(param)]}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert response.data[0][str(param)] == data[str(param)]
    for param in ['color', 'brand_name', 'car_model_name']:
        data = {str(param): test_instance[str(param)]}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert data[str(param)] in response.data[0][str(param)]
    for param in ['engine_volume', 'demand_level']:
        data = {f'max_{param}': test_instance[str(param)]}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(param)]) <= float(data[f'max_{param}'])
        data = {f'min_{param}': test_instance[str(param)]}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(param)]) >= float(data[f'min_{param}'])
    data = {'max_year_of_production': test_instance['year_of_production']}
    response = client.get(reverse('car-list'), data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_production'] <= data['max_year_of_production']
    data = {'min_year_of_production': test_instance['year_of_production']}
    response = client.get(reverse('car-list'), data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_production'] >= data['min_year_of_production']
    bad_data = {'engine_volume': 1000}
    response = client.get(reverse('car-list'), data=bad_data)
    assert response.status_code == 200
    assert response.data == []
    bad_data = {'max_year_of_production': 1000}
    response = client.get(reverse('car-list'), data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('verified_user', ['DEALER'], indirect=True)
def test_market_search_filters(client, verified_user, cars):
    client.force_authenticate(user=verified_user['user_instance'])
    response = client.get(reverse('car-list'))
    test_instance = response.data[3]
    for param in ['brand_name', 'car_model_name']:
        data = {'search': test_instance[str(param)]}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert response.data[0][str(param)] == data['search']
    data = {'max_year_of_production': test_instance['year_of_production'],
            'search': test_instance['brand_name']}
    response = client.get(reverse('car-list'), data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_production'] <= data['max_year_of_production']
    assert response.data[0]['brand_name'] == data['search']
    bad_data = {'search': 'Puppindui'}
    response = client.get(reverse('car-list'), data=bad_data)
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.parametrize('verified_user', ['SELLER'], indirect=True)
def test_market_order_filters(client, verified_user, cars):
    client.force_authenticate(user=verified_user['user_instance'])
    response = client.get(reverse('car-list'))
    test_instance = response.data[3]
    for param in ['engine_volume', 'year_of_production', 'demand_level']:
        data = {'ordering': str(param)}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(param)]) <= float(response.data[1][str(param)])
        data = {'ordering': f'-{str(param)}'}
        response = client.get(reverse('car-list'), data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(param)]) >= float(response.data[1][str(param)])
    data = {'max_year_of_production': test_instance['year_of_production'],
            'ordering': 'engine_volume'}
    response = client.get(reverse('car-list'), data=data)
    assert response.status_code == 200
    assert response.data[0]['year_of_production'] <= data['max_year_of_production']
    assert float(response.data[0]['engine_volume']) <= float(response.data[1]['engine_volume'])
