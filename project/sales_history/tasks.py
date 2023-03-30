"""This module contains celery task for purchases of suitable for dealer cars"""

from decimal import Decimal

from car_market.models import MarketAvailableCarModel
from car_park.models import DealerCarParkModel, SellerCarParkModel
from car_spec.models import DealerSuitableCarModel, DealerSuitableSellerModel
from car_spec.serializers import (DealerSuitableCarModelsSerializer,
                                  DealerSuitableSellerSerializer)
from celery import shared_task
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from promo.models import SellerPromoModel
from promo.serializers import SellersPromoSerializer
from user.models import AutoDealerModel, DealerFromSellerPurchaseNumber

from .models import SellerSalesHistoryModel


def selected_and_promo_car_prices_collector(promos: QuerySet[SellerPromoModel],
                                            suitable_cars: list[int],
                                            best_sellers: list[int],
                                            best_seller_cars: list[int]) -> \
        list[dict[str, SellerCarParkModel | Decimal]] | list:
    """Takes promo models, list of suitable for dealer cars, list of suitable for dealer sellers,
    list of suitable seller's cars to buy and returns list of possible car prices (with or without
    promo) for each evaluated seller car park (or empty list if there is no such cars in parks)"""
    car_prices = []
    for promo in promos:
        promo_data = SellersPromoSerializer(promo).data
        promo_discount = Decimal(promo_data['discount_size'])
        promo_car_parks = [SellerCarParkModel.objects.get(id=car_park_id) for car_park_id
                           in promo_data["promo_cars"] if
                           SellerCarParkModel.objects.get(id=car_park_id).car_model.pk
                           in suitable_cars]
        for park in promo_car_parks:
            car_prices.append({'car_park': park,
                               'price': Decimal(park.car_price * (100 -
                                                                  promo_discount) / 100)})
    for seller in best_sellers:
        seller_park = SellerCarParkModel.objects.filter(seller=seller,
                                                        car_model__in=best_seller_cars)
        for park in seller_park:
            car_prices.append({'car_park': park,
                               'price': Decimal(park.car_price)})
    return car_prices


def best_deal_finder(car_prices: list) -> list[dict[str,
                                                    SellerCarParkModel |
                                                    MarketAvailableCarModel |
                                                    Decimal]] | None:
    """Takes list of possible car prices and returns best deal possible deal to
    make or None if there are no possible prices"""
    chosen_deals = None
    if car_prices:
        best_price = min(price['price'] for price in car_prices)
        chosen_deals = [{'seller_park': car_price['car_park'],
                         'car': car_price['car_park'].car_model,
                         'price': car_price['price']}
                        for car_price in car_prices
                        if car_price['price'] == best_price]
    return chosen_deals


def make_a_deal_and_create_dealer_park(chosen_deal: dict,
                                       dealer: AutoDealerModel,
                                       margin_size: int):
    """Takes the chosen deal, dealer model and size of margin to adjust on bought cars and
    makes a deal within passed in parameters, creates history records about the deal made"""
    balance = dealer.balance
    seller_park = chosen_deal['seller_park']
    bought_cars_number = 0
    while balance > chosen_deal['price']:
        bought_cars_number = bought_cars_number + 1
        balance = balance - chosen_deal['price']
    if bought_cars_number:
        with transaction.atomic():
            dealer_park = DealerCarParkModel.objects. \
                create(dealer=dealer,
                       car_model=chosen_deal['car'],
                       car_price=chosen_deal['price'] * Decimal((100 + margin_size) / 100),
                       available_number=0)
            dealer.balance = balance
            dealer.save()
            seller_park.available_number = seller_park.available_number - bought_cars_number
            seller_park.save()
            dealer_park.available_number = bought_cars_number
            dealer_park.save()
            SellerSalesHistoryModel.objects.create(seller=seller_park.seller,
                                                   sold_car_model=seller_park,
                                                   car_buyer=dealer,
                                                   selling_price=chosen_deal['price'],
                                                   sold_cars_quantity=bought_cars_number,
                                                   deal_sum=bought_cars_number *
                                                   chosen_deal['price'])
            purchase_number_model = \
                DealerFromSellerPurchaseNumber.objects.get_or_create(seller=seller_park.seller,
                                                                     dealer=dealer)[0]
            current_purchase_number = int(purchase_number_model.purchase_number)
            purchase_number_model.purchase_number = \
                current_purchase_number + bought_cars_number
            purchase_number_model.save()


@shared_task(name='purchase_cars_for_dealers')
def task_dealer_cars_purchase():
    """Celery script that checks car market for all dealers having suitable cars/sellers model
    filled and makes best precalculated deals (of cars purchase) if there are some taking in
    account current seller promos"""
    for ready_dealer in DealerSuitableSellerModel.objects.all():
        dealer = ready_dealer.dealer
        best_seller_cars = DealerSuitableSellerSerializer(ready_dealer).data['deal_car_models']
        best_sellers = DealerSuitableSellerSerializer(ready_dealer).data["suitable_seller"]
        suit_cars_model = DealerSuitableCarModel.objects.get(dealer=dealer)
        suit_cars_list = DealerSuitableCarModelsSerializer(suit_cars_model).data['car_model']
        promos = SellerPromoModel.objects.filter(end_date__gte=timezone.now(),
                                                 start_date__lte=timezone.now(),
                                                 promo_cars__car_model__in=suit_cars_list,
                                                 promo_aims__in=[dealer.id])
        car_prices = selected_and_promo_car_prices_collector(promos,
                                                             suit_cars_list,
                                                             best_sellers,
                                                             best_seller_cars)
        if car_prices:
            chosen_deals = best_deal_finder(car_prices)
            if chosen_deals:
                chosen_deal = chosen_deals[0]
                make_a_deal_and_create_dealer_park(chosen_deal, dealer, 20)
