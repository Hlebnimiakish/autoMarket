# pylint: skip-file

from decimal import Decimal

import pytest
from sales_history.models import CarBuyerHistoryModel

from .tasks import task_make_deal_from_offer

pytestmark = pytest.mark.django_db(transaction=True)


def test_task_make_deal_from_offer_from_view(control_case_dealers_parks_offer,
                                             celery_app,
                                             celery_worker,
                                             client):
    offer_data = control_case_dealers_parks_offer['offer_data']
    chosen_park = control_case_dealers_parks_offer['predefined_park']
    buyer_id = offer_data['creator']
    records = CarBuyerHistoryModel.objects.filter(buyer_id=buyer_id)
    assert not bool(records)
    task_make_deal_from_offer.delay(offer_data)
    records = CarBuyerHistoryModel.objects.filter(buyer_id=buyer_id)
    assert bool(records)
    record = CarBuyerHistoryModel.objects.get(buyer_id=buyer_id)
    assert record.bought_car_model == chosen_park
    assert record.bought_car_model.car_model == chosen_park.car_model
    assert Decimal(record.car_price) <= Decimal(offer_data['max_price'])
