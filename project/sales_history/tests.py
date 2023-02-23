import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_buyer_can_view_his_purchase_history(history_records,
                                             client):
    user = history_records['buyer'].buyer.user
    id = history_records['buyer'].pk
    client.force_authenticate(user)
    response = client.get(reverse('my-purchase-history-list'))
    assert response.status_code == 200
    assert response.data[0]['car_price']
    response = client.get(reverse('my-purchase-history-detail',
                                  kwargs={'pk': id}))
    assert response.status_code == 200
    assert response.data['deal_sum']


def test_seller_and_dealer_can_view_his_sales_history(history_records,
                                                      client):
    users_with_records = {'dealer': history_records['dealer'].dealer.user,
                          'seller': history_records['seller'].seller.user}
    for user_type, user in users_with_records.items():
        id = history_records[str(user_type)].pk
        client.force_authenticate(user)
        response = client.get(reverse(f'my-{user_type}-sales-history-list'))
        assert response.status_code == 200
        assert response.data[0]['selling_price']
        response = client.get(reverse(f'my-{user_type}-sales-history-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 200
        assert response.data['deal_sum']


def test_other_users_can_not_view_dealer_sales_history(history_records,
                                                       client):
    for user in [history_records['buyer'].buyer.user,
                 history_records['seller'].seller.user]:
        id = history_records['dealer'].pk
        client.force_authenticate(user)
        response = client.get(reverse('my-dealer-sales-history-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-dealer-sales-history-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 403


def test_other_users_can_not_view_seller_sales_history(history_records,
                                                       client):
    for user in [history_records['buyer'].buyer.user,
                 history_records['dealer'].dealer.user]:
        id = history_records['seller'].pk
        client.force_authenticate(user)
        response = client.get(reverse('my-seller-sales-history-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-seller-sales-history-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 403


def test_other_users_can_not_view_buyer_purchase_history(history_records,
                                                         client):
    for user in [history_records['dealer'].dealer.user,
                 history_records['seller'].seller.user]:
        id = history_records['dealer'].pk
        client.force_authenticate(user)
        response = client.get(reverse('my-purchase-history-list'))
        assert response.status_code == 403
        response = client.get(reverse('my-purchase-history-detail',
                                      kwargs={'pk': id}))
        assert response.status_code == 403
