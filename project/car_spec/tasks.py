"""This module contains celery tasks for defining dealer-seller relations"""

from contextlib import suppress
from decimal import Decimal

from car_market.models import MarketAvailableCarModel
from car_park.models import SellerCarParkModel
from discount.models import RegularCustomerDiscountLevelsModel
from root.celery import app
from user.models import AutoDealerModel, DealerFromSellerPurchaseNumber

from .models import (DealerSearchCarSpecificationModel, DealerSuitableCarModel,
                     DealerSuitableSellerModel)
from .serializers import (DealerSearchCarSpecificationEstFieldsSerializer,
                          DealerSuitableCarModelsSerializer)


@app.tasks
def task_find_suit_cars_for_all_dealers():
    """Celery script that checks all dealer specifications parameters,
    finds suitable car models and adds suitable cars to corresponding model"""
    for spec in DealerSearchCarSpecificationModel.objects.all():
        dealer = spec.dealer
        spec_data = DealerSearchCarSpecificationEstFieldsSerializer(spec).data
        suit_cars = DealerSuitableCarModel.objects.get_or_create(dealer=dealer)[0]
        suit_cars.car_model.clear()
        str_list = ['transmission', 'body_type', 'engine_fuel_type', 'drive_unit', 'color']
        bool_params = ["safe_controls", "parking_help", "climate_controls",
                       "multimedia", "additional_safety", "other_additions"]
        spec_actual_data = {}
        for key, value in spec_data.items():
            if key in str_list:
                spec_actual_data[key] = value
            if key in bool_params and value:
                spec_actual_data[key] = value
        cars = MarketAvailableCarModel.\
            objects.filter(engine_volume__gte=spec_data['engine_volume'],
                           year_of_production__gte=spec_data['min_year_of_production'],
                           **spec_actual_data)
        cars = list(cars)
        suit_cars.car_model.add(*cars)


@app.tasks
def task_find_suit_cars_for_dealer(spec: DealerSearchCarSpecificationModel):
    """Celery script that takes specification model, checks it's parameters,
    finds suitable car models and adds suitable cars to corresponding model"""
    dealer = spec.dealer
    spec_data = DealerSearchCarSpecificationEstFieldsSerializer(spec).data
    suit_cars = DealerSuitableCarModel.objects.get_or_create(dealer=dealer)[0]
    suit_cars.car_model.clear()
    str_list = ['transmission', 'body_type', 'engine_fuel_type', 'drive_unit', 'color']
    bool_params = ["safe_controls", "parking_help", "climate_controls",
                   "multimedia", "additional_safety", "other_additions"]
    spec_actual_data = {}
    for key, value in spec_data.items():
        if key in str_list:
            spec_actual_data[key] = value
        if key in bool_params and value:
            spec_actual_data[key] = value
    cars = MarketAvailableCarModel. \
        objects.filter(engine_volume__gte=spec_data['engine_volume'],
                       year_of_production__gte=spec_data['min_year_of_production'],
                       **spec_actual_data)
    cars = list(cars)
    suit_cars.car_model.add(*cars)


def purchase_map_creator(discount_map: dict, current_purchase_number: int) -> dict[int, int]:
    """Takes seller discount map and number of dealer purchases (from this seller) and
    returns map with discount levels and future number of purchases to make within
    each level"""
    sorted_discounts_list = sorted([int(purchase_number) for
                                    purchase_number in discount_map.keys()],
                                   reverse=True)
    purchase_map = {}
    purchases = 100
    for purchase_number in sorted_discounts_list:
        if current_purchase_number < purchase_number \
                < current_purchase_number + 100:
            index = sorted_discounts_list.index(purchase_number)
            if index < (len(sorted_discounts_list) - 1):
                diff = purchase_number - sorted_discounts_list[index + 1]
                purchase_map[sorted_discounts_list[index + 1]] = diff
                purchases = purchases - diff
            else:
                purchase_map[0] = purchase_number
                purchases = purchases - purchase_number
    if purchases > 0:
        purchase_map[sorted_discounts_list[0]] = purchases
    return purchase_map


def deal_sum_calculator(discount_map: dict, current_purchase_number: int,
                        car_price: Decimal) -> Decimal:
    """Takes seller discount map and number of dealer purchases (from this seller) and
    price of the estimating car and returns value of the potential car purchase deal"""
    purchase_map = purchase_map_creator(discount_map, current_purchase_number)
    deal_sum = Decimal()
    for level in list(purchase_map.keys()):
        if level in list(discount_map.keys()):
            deal_sum = \
                deal_sum + Decimal(car_price) * \
                (100 - discount_map[str(level)]) / 100 * purchase_map[level]
        else:
            deal_sum = \
                deal_sum + Decimal(car_price) * purchase_map[level]
    return deal_sum


def deals_collector(suitable_cars_list: list[MarketAvailableCarModel],
                    dealer: AutoDealerModel) -> list[dict]:
    """Takes list of suitable for dealer cars and dealer model itself and returns
    list of possible car purchase deals for passed in dealer"""
    deals = []
    for car in suitable_cars_list:
        for park in SellerCarParkModel.objects.filter(car_model=car):
            discount_levels = None
            # pylint: disable=no-member
            with suppress(RegularCustomerDiscountLevelsModel.DoesNotExist):
                discount_levels = RegularCustomerDiscountLevelsModel. \
                    objects.get(seller=park.seller)
            if discount_levels:
                discount_map = discount_levels.purchase_number_discount_map
                current_purchase_number = 0
                # pylint: disable=no-member
                with suppress(DealerFromSellerPurchaseNumber.DoesNotExist):
                    current_purchase_number = \
                        int(DealerFromSellerPurchaseNumber.
                            objects.get(seller=park.seller,
                                        dealer=dealer).purchase_number)
                deal_sum = deal_sum_calculator(discount_map,
                                               current_purchase_number,
                                               park.car_price)
                deals.append({'seller': park.seller,
                              'deal_sum': deal_sum,
                              'car_model': park.car_model})
            else:
                deal_sum = Decimal(park.car_price) * 100
                deals.append({'seller': park.seller,
                              'deal_sum': deal_sum,
                              'car_model': park.car_model})
    return deals


def suitable_seller_with_suitable_cars_adder(deals: list[dict],
                                             suit_seller: DealerSuitableSellerModel):
    """Takes list of possible deals and suitable for dealer sellers/cars model,
    finds and adds best suitable sellers and cars to corresponding model"""
    best_deal_sum = min(deal['deal_sum'] for deal in deals)
    suit_sellers_list = []
    deal_car_models = []
    for deal in deals:
        if deal['deal_sum'] == best_deal_sum:
            suit_sellers_list.append(deal['seller'])
            deal_car_models.append(deal['car_model'])
    suit_seller.suitable_seller.add(*suit_sellers_list)
    suit_seller.deal_car_models.add(*deal_car_models)


@app.tasks
def task_find_suitable_sellers():
    """Celery script that checks all suitable within dealer car specification parameters
    cars and adds suitable (which makes the best possible deals) for dealer
    sellers/cars to corresponding model"""
    for suitable_cars in DealerSuitableCarModel.objects.all():
        dealer = suitable_cars.dealer
        cars_list = DealerSuitableCarModelsSerializer(suitable_cars).data['car_model']
        suit_seller = DealerSuitableSellerModel.objects.get_or_create(dealer=dealer)[0]
        suit_seller.suitable_seller.clear()
        deals = deals_collector(cars_list, dealer)
        if deals:
            suitable_seller_with_suitable_cars_adder(deals, suit_seller)
