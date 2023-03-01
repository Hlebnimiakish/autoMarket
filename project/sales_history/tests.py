from datetime import datetime

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


def test_dealer_and_seller_history_filters(history_records,
                                           dealer_history_record,
                                           seller_history_record,
                                           all_profiles,
                                           client):
    add_records = {"dealer": dealer_history_record,
                   "seller": seller_history_record}
    for k, v in add_records.items():
        user = all_profiles[str(k)]['profile_instance'].user
        client.force_authenticate(user=user)
        data = {"before_date": v['record_instance'].date}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=data)
        assert response.status_code == 200
        assert datetime.strptime(response.data[0]['date'], '%Y-%m-%d').date() \
               <= data["before_date"]
        data = {"after_date": v['record_instance'].date}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=data)
        assert response.status_code == 200
        assert datetime.strptime(response.data[0]['date'], '%Y-%m-%d').date() \
               >= data["after_date"]
        for field in ['selling_price', 'sold_cars_quantity', 'deal_sum']:
            data = {f'min_{field}': v['record_data'][str(field)]}
            response = client.get(reverse(f'my-{k}-sales-history-list'),
                                  data=data)
            assert response.status_code == 200
            assert float(response.data[0][str(field)]) >= \
                   float(data[f'min_{field}'])
            data = {f'max_{field}': v['record_data'][str(field)]}
            response = client.get(reverse(f'my-{k}-sales-history-list'),
                                  data=data)
            assert response.status_code == 200
            assert float(response.data[0][str(field)]) <= \
                   float(data[f'max_{field}'])
        for field in ['sold_car_model', 'car_buyer', 'selling_price',
                      'sold_cars_quantity', 'deal_sum']:
            data = {str(field): v['record_data'][str(field)]}
            response = client.get(reverse(f'my-{k}-sales-history-list'),
                                  data=data)
            assert response.status_code == 200
            assert response.data[0][str(field)] >= data[str(field)]
        bad_data = {"selling_price": 100000000}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=bad_data)
        assert response.status_code == 200
        assert response.data == []


def test_buyer_history_filters(history_records,
                               buyer_history_record,
                               all_profiles,
                               client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    data = {"before_date": buyer_history_record['record_instance'].date}
    response = client.get(reverse('my-purchase-history-list'),
                          data=data)
    assert response.status_code == 200
    assert datetime.strptime(response.data[0]['date'], '%Y-%m-%d').date() \
           <= data["before_date"]
    data = {"after_date": buyer_history_record['record_instance'].date}
    response = client.get(reverse('my-purchase-history-list'),
                          data=data)
    assert response.status_code == 200
    assert datetime.strptime(response.data[0]['date'], '%Y-%m-%d').date() \
           >= data["after_date"]
    for field in ['bought_quantity', 'car_price', 'deal_sum']:
        data = {f'min_{field}': buyer_history_record['record_data'][str(field)]}
        response = client.get(reverse('my-purchase-history-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(field)]) >= \
               float(data[f'min_{field}'])
        data = {f'max_{field}': buyer_history_record['record_data'][str(field)]}
        response = client.get(reverse('my-purchase-history-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(field)]) <= \
               float(data[f'max_{field}'])
    for field in ['bought_car_model', 'auto_dealer', 'bought_quantity',
                  'car_price', 'deal_sum']:
        data = {str(field): buyer_history_record['record_data'][str(field)]}
        response = client.get(reverse('my-purchase-history-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0][str(field)] >= data[str(field)]
    bad_data = {"car_price": 100000000}
    response = client.get(reverse('my-purchase-history-list'),
                          data=bad_data)
    assert response.status_code == 200
    assert response.data == []


def test_dealer_and_seller_search_history_filters(history_records,
                                                  dealer_history_record,
                                                  seller_history_record,
                                                  all_profiles,
                                                  client):
    add_records = {"dealer": dealer_history_record,
                   "seller": seller_history_record}
    for k, v in add_records.items():
        user = all_profiles[str(k)]['profile_instance'].user
        client.force_authenticate(user=user)
        car = v['record_instance'].sold_car_model.car_model.car_model_name
        data = {'search': str(car)}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=data)
        assert response.status_code == 200
        assert v['record_instance'].sold_car_model.id in \
               [car['sold_car_model'] for car in response.data]


def test_buyer_search_history_filters(history_records,
                                      buyer_history_record,
                                      all_profiles,
                                      client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    car = buyer_history_record['record_instance'].bought_car_model.car_model.car_model_name
    data = {'search': str(car)}
    response = client.get(reverse('my-purchase-history-list'),
                          data=data)
    assert response.status_code == 200
    assert buyer_history_record['record_instance'].bought_car_model.id in \
           [car['bought_car_model'] for car in response.data]


def test_dealer_and_seller_order_history_filters(history_records,
                                                 dealer_history_record,
                                                 seller_history_record,
                                                 all_profiles,
                                                 client):
    add_records = {"dealer": dealer_history_record,
                   "seller": seller_history_record}
    for k, v in add_records.items():
        user = all_profiles[str(k)]['profile_instance'].user
        client.force_authenticate(user=user)
        for field in ['deal_sum', 'sold_cars_quantity', 'selling_price']:
            data = {'ordering': str(field)}
            response = client.get(reverse(f'my-{k}-sales-history-list'),
                                  data=data)
            assert response.status_code == 200
            assert float(response.data[0][str(field)]) <= \
                   float(response.data[1][str(field)])
            data = {'ordering': f'-{str(field)}'}
            response = client.get(reverse(f'my-{k}-sales-history-list'),
                                  data=data)
            assert response.status_code == 200
            assert float(response.data[0][str(field)]) >= \
                   float(response.data[1][str(field)])
        data = {'ordering': 'date'}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0]['date'] <= response.data[1]['date']
        data = {'ordering': '-date'}
        response = client.get(reverse(f'my-{k}-sales-history-list'),
                              data=data)
        assert response.status_code == 200
        assert response.data[0]['date'] >= response.data[1]['date']


def test_buyer_order_history_filters(history_records,
                                     buyer_history_record,
                                     all_profiles,
                                     client):
    user = all_profiles['buyer']['profile_instance'].user
    client.force_authenticate(user=user)
    for field in ['deal_sum', 'bought_quantity', 'car_price']:
        data = {'ordering': str(field)}
        response = client.get(reverse('my-purchase-history-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(field)]) <= \
               float(response.data[1][str(field)])
        data = {'ordering': f'-{str(field)}'}
        response = client.get(reverse('my-purchase-history-list'),
                              data=data)
        assert response.status_code == 200
        assert float(response.data[0][str(field)]) >= \
               float(response.data[1][str(field)])
    data = {'ordering': 'date'}
    response = client.get(reverse('my-purchase-history-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['date'] <= response.data[1]['date']
    data = {'ordering': '-date'}
    response = client.get(reverse('my-purchase-history-list'),
                          data=data)
    assert response.status_code == 200
    assert response.data[0]['date'] >= response.data[1]['date']
