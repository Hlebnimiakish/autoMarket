import uuid
from datetime import timedelta
from random import choice

import pytest
from django.utils import timezone

from .models import DealerPromoModel, SellerPromoModel
from .serializers import DealersPromoSerializer, SellersPromoSerializer


@pytest.fixture(scope='function', name='promo_data')
def create_promo_data():
    promo_data = {
        "promo_name": f"promo{uuid.uuid4().hex}",
        "promo_description": "This promo is a test promo",
        "start_date": timezone.now(),
        "end_date": (timezone.now() + timedelta(days=5)),
        "discount_size": choice([3, 5, 10, 15, 20]),
    }
    return promo_data


@pytest.fixture(scope='function', name='dealer_promo')
def create_dealer_promo(all_profiles, car_parks, promo_data):
    promo_data['creator'] = \
        all_profiles['dealer']['profile_instance']
    dealer_promo = DealerPromoModel.objects.create(**promo_data)
    dealer_promo.promo_cars.add(car_parks['dealer_park'])
    dealer_promo.promo_aims.add(all_profiles['buyer']['profile_instance'])
    dealer_promo_data = DealersPromoSerializer(dealer_promo).data
    return {'promo': dealer_promo,
            'promo_data': dealer_promo_data}


@pytest.fixture(scope='function', name='seller_promo')
def create_seller_promo(all_profiles, car_parks, promo_data):
    promo_data['creator'] = \
        all_profiles['seller']['profile_instance']
    seller_promo = SellerPromoModel.objects.create(**promo_data)
    seller_promo.promo_cars.add(car_parks['seller_park'])
    seller_promo.promo_aims.add(all_profiles['dealer']['profile_instance'])
    seller_promo_data = SellersPromoSerializer(seller_promo).data
    return {'promo': seller_promo,
            'promo_data': seller_promo_data}
