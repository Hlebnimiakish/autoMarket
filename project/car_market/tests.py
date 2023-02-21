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
