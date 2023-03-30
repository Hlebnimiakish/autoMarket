"""This module contains celery tasks for purchases of buyer selected cars (via offers)"""

from decimal import Decimal

from car_park.models import DealerCarParkModel
from celery import shared_task
from django.db import transaction
from django.db.models import ForeignKey
from django.utils import timezone
from promo.models import DealerPromoModel
from promo.serializers import DealersPromoSerializer
from sales_history.models import CarBuyerHistoryModel, DealerSalesHistoryModel
from user.models import BuyerFromDealerPurchaseNumber, CarBuyerModel

from .models import OfferModel
from .serializers import OffersSerializer


def select_park_to_buy_from(offer: dict, buyer: CarBuyerModel) -> dict | None:
    """Takes offer model and passes list of suitable car parks to prices evaluating
    function, returns car park with best offered price on market"""
    offer_car = offer['car_model']
    offer_price = Decimal(offer["max_price"])
    suitable_car_parks = DealerCarParkModel.objects.filter(car_model=offer_car,
                                                           available_number__gt=0)
    suitable_car_parks_list = list(suitable_car_parks)
    return find_best_park_by_price_from_suitable_car_parks(buyer,
                                                           suitable_car_parks_list,
                                                           offer_price)


def find_best_park_by_price_from_suitable_car_parks(buyer: CarBuyerModel,
                                                    suitable_car_parks_list:
                                                    list[DealerCarParkModel],
                                                    offer_price: Decimal) -> dict | None:
    """Takes car buyer model, list of car parks selling suitable car and max price of the offer,
    if there are suitable cars on market, returns best park with minimal price to buy from"""
    selected_park = None
    if suitable_car_parks_list:
        promos = DealerPromoModel.objects.filter(promo_cars__in=suitable_car_parks_list,
                                                 promo_aims__in=[buyer],
                                                 end_date__gte=timezone.now(),
                                                 start_date__lte=timezone.now())
        car_park_prices_with_promo = []
        promo_parks_list = []
        for park in suitable_car_parks_list:
            for promo in promos:
                promo_cars = DealersPromoSerializer(promo).data['promo_cars']
                if park.pk in promo_cars:
                    actual_price = Decimal(park.car_price) * \
                                   (100 - Decimal(promo.discount_size)) / 100
                    if actual_price <= offer_price:
                        promo_parks_list.append(park)
                        car_park_prices_with_promo.append({"park": park,
                                                           "actual_price": actual_price})
        car_park_prices_without_promo = [{"park": park,
                                          "actual_price": Decimal(park.car_price)}
                                         for park in suitable_car_parks_list
                                         if park not in promo_parks_list and
                                         Decimal(park.car_price) <= offer_price]
        all_prices = car_park_prices_without_promo + car_park_prices_with_promo
        if all_prices:
            the_lowest_car_price = min(price['actual_price'] for price in all_prices)
            parks_to_buy_from = [price for price in all_prices
                                 if price['actual_price'] == the_lowest_car_price]
            selected_park = parks_to_buy_from[0]
    return selected_park


def make_offer_deal(selected_park: dict,
                    buyer: CarBuyerModel | ForeignKey,
                    offer_instance: OfferModel):
    """Takes selected dealer car park to buy from and car buyer model and makes
    a deal of car purchase, creates history records of car bought and sold for
    buyer and dealer"""
    dealer = selected_park['park'].dealer
    with transaction.atomic():
        car_price = selected_park['actual_price']
        park = selected_park['park']
        park.available_number = int(park.available_number) - 1
        dealer.balance = Decimal(dealer.balance) + car_price
        dealer.save()
        park.save()
        DealerSalesHistoryModel.objects.create(dealer=dealer,
                                               sold_car_model=park,
                                               car_buyer=buyer,
                                               selling_price=car_price,
                                               sold_cars_quantity=1,
                                               deal_sum=car_price)
        CarBuyerHistoryModel.objects.create(bought_car_model=park,
                                            auto_dealer=dealer,
                                            bought_quantity=1,
                                            car_price=car_price,
                                            deal_sum=car_price,
                                            buyer=buyer)
        offer_instance.is_active = False
        offer_instance.save()
        purchase_number_model = \
            BuyerFromDealerPurchaseNumber.objects.get_or_create(buyer=buyer,
                                                                dealer=dealer)[0]
        current_purchase_number = int(purchase_number_model.purchase_number)
        purchase_number_model.purchase_number = current_purchase_number + 1
        purchase_number_model.save()


@shared_task(name='make_deal_from_offer')
def task_make_deal_from_offer(offer: dict):
    """Celery script that takes an offer and search for best possible deal to
    buy a car on minimal suitable price, if currently there is no purchase options
    waits 5 minutes before next check for the same offer"""
    buyer = CarBuyerModel.objects.get(id=offer["creator"])
    selected_park = select_park_to_buy_from(offer, buyer)
    buyer_balance = Decimal(buyer.balance)
    if selected_park and selected_park['actual_price'] <= buyer_balance:
        offer_instance = OfferModel.objects.get(id=offer['id'])
        make_offer_deal(selected_park, buyer, offer_instance)
    else:
        check_offer = OfferModel.objects.get_or_none(id=offer['id'])
        if check_offer:
            offer_data = OffersSerializer(check_offer).data
            task_make_deal_from_offer.apply_async([offer_data], countdown=300)
