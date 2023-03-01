import uuid
from datetime import timedelta
from random import choice, randint

import pytest
from car_park.models import DealerCarParkModel, SellerCarParkModel
from django.utils import timezone
from user.models import AutoDealerModel, AutoSellerModel, CustomUserModel

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


@pytest.fixture(scope='function', name='additional_promo')
def create_additional_promo(request, dealer_profile, seller_profile,
                            all_profiles, cars):
    password = uuid.uuid4().hex
    filler = uuid.uuid4().hex
    user_data = {
        "username": f"test{filler}",
        "password": f"pass{password}",
        "email": f"test{filler}@am.com",
        "user_type": str.upper(request.param),
        "is_verified": True
    }
    user = CustomUserModel.objects.create_user(**user_data)
    profiles = {'dealer': dealer_profile, 'seller': seller_profile}
    profile_models = {'dealer': AutoDealerModel, 'seller': AutoSellerModel}
    profile = profiles[str(request.param)]
    profile['user'] = user
    profile = profile_models[str(request.param)].objects.create(**profile)
    models = {'dealer': DealerPromoModel,
              'seller': SellerPromoModel}
    serializers = {'dealer': DealersPromoSerializer,
                   'seller': SellersPromoSerializer}
    parks = {'dealer': DealerCarParkModel,
             'seller': SellerCarParkModel}
    aims = {'dealer': all_profiles['buyer']['profile_instance'],
            'seller': all_profiles['dealer']['profile_instance']}
    owner = profile
    promo_data = {
        "promo_name": f"promo{uuid.uuid4().hex}",
        "promo_description": "This promo is a test promo",
        "start_date": timezone.now(),
        "end_date": (timezone.now() + timedelta(days=5)),
        "discount_size": choice([3, 5, 10, 15, 20]),
        "creator": owner
    }
    promo = models[str(request.param)].objects.create(**promo_data)
    park_data = {
        "car_model": choice([c for c in cars]),
        "available_number": randint(1, 10),
        "car_price": randint(1000, 10000),
        str(request.param): owner
    }
    park = parks[str(request.param)].objects.create(**park_data)
    promo.promo_cars.add(park)
    promo.promo_aims.add(aims[str(request.param)])
    promo_data = serializers[str(request.param)](promo).data
    return {'promo_instance': promo,
            'promo_data': promo_data}
