# pylint: skip-file

"""This module contains fixtures for statistics tasks test"""

import datetime
import uuid
from decimal import Decimal
from random import choice, randint
from typing import Type

import pytest
from car_market.models import MarketAvailableCarModel
from car_park.models import DealerCarParkModel, SellerCarParkModel
from django.db.models import ForeignKey
from sales_history.models import (CarBuyerHistoryModel,
                                  DealerSalesHistoryModel,
                                  SellerSalesHistoryModel)
from user.models import (AutoDealerModel, AutoSellerModel,
                         BuyerFromDealerPurchaseNumber, CarBuyerModel,
                         CustomUserModel, DealerFromSellerPurchaseNumber)


@pytest.fixture(scope='function', name='predefined_stats_data_generator')
def create_dealers_and_sellers_and_their_car_parks(cars) -> \
        dict[str,
             dict[int,
                  dict[str, int | str | MarketAvailableCarModel | None]]]:
    """Creates users, dealers, sellers, their car parks, buyers all those user's history
    records, records about purchase numbers and other data needed for statistics calculation
    and returns dict with predefined statistics data for each user for statistics calculation
    tasks test"""

    def generate_user(user_type: str) -> CustomUserModel:
        """Creates and returns user instance of given type"""
        user_data = {
            "username": f"test{uuid.uuid4().hex}",
            "password": f"pass{uuid.uuid4().hex}",
            "email": f"test{uuid.uuid4().hex}@am.com",
            "user_type": user_type,
            "is_verified": True
        }
        user = CustomUserModel.objects.create_user(**user_data)
        return user

    def car_park_generator(user_type: str,
                           user_profile:
                           AutoDealerModel | AutoSellerModel,
                           park_model_type:
                           Type[DealerCarParkModel | SellerCarParkModel]) \
            -> SellerCarParkModel | DealerCarParkModel:
        """Generates and returns car park instance"""
        park_data = {
            "car_model": choice(list(cars)),
            "available_number": 100,
            "car_price": 100,
            user_type: user_profile
        }
        park = park_model_type.objects.create(**park_data)
        return park

    date = datetime.date.today() - datetime.timedelta(days=2)
    seller_parks = []
    dealer_parks = []
    buyers = []
    for _ in range(3):
        dealer_profile_data = {
            "name": f"tdealer{uuid.uuid4().hex}",
            "home_country": "AL",
            "user": generate_user('DEALER'),
            "balance": 1000000
        }
        dealer = AutoDealerModel.objects.create(**dealer_profile_data)
        dealer_park = car_park_generator("dealer", dealer, DealerCarParkModel)
        dealer_parks.append(dealer_park)
        seller_profile_data = {
            "name": f"tseller{uuid.uuid4().hex}",
            "year_of_creation": randint(1000, 2023),
            "user": generate_user('SELLER')
        }
        seller = AutoSellerModel.objects.create(**seller_profile_data)
        seller_park = car_park_generator("seller", seller, SellerCarParkModel)
        seller_parks.append(seller_park)
        buyer_profile_data = {
            "firstname": f"tbuyer{uuid.uuid4().hex}",
            "lastname": f"tbuyer{uuid.uuid4().hex}",
            "drivers_license_number": str(uuid.uuid4().hex),
            "balance": 100000,
            "user": generate_user('BUYER')
        }
        buyer = CarBuyerModel.objects.create(**buyer_profile_data)
        buyers.append(buyer)

    def dealer_seller_purchase_number_generator(seller: ForeignKey,
                                                dealer: ForeignKey,
                                                purchase_number: int):
        """Generates record with number of dealer from seller purchases"""
        purchase_number_record = {
            "seller": seller,
            "dealer": dealer,
            "purchase_number": purchase_number
        }
        DealerFromSellerPurchaseNumber.objects.create(**purchase_number_record)

    def seller_history_record_generator(seller: ForeignKey,
                                        buyer: ForeignKey,
                                        sold_cars_quantity: int,
                                        selling_price: Decimal,
                                        sold_car_model: SellerCarParkModel):
        """Generates seller history record"""
        record_data = {
            "sold_cars_quantity": sold_cars_quantity,
            "selling_price": selling_price,
            "deal_sum": sold_cars_quantity * selling_price,
            "sold_car_model": sold_car_model,
            "car_buyer": buyer,
            "seller": seller
        }
        record = SellerSalesHistoryModel.objects.create(**record_data)
        record.date = date
        record.save()

    def dealer_history_record_generator(dealer: ForeignKey,
                                        buyer: ForeignKey,
                                        sold_cars_quantity: int,
                                        selling_price: Decimal,
                                        sold_car_model: DealerCarParkModel):
        """Generates dealer history record"""
        record_data = {
            "sold_cars_quantity": sold_cars_quantity,
            "selling_price": selling_price,
            "deal_sum": sold_cars_quantity * selling_price,
            "sold_car_model": sold_car_model,
            "car_buyer": buyer,
            "dealer": dealer
        }
        record = DealerSalesHistoryModel.objects.create(**record_data)
        record.date = date
        record.save()

    predefined_seller_data = {}
    predefined_dealer_data = {}
    predefined_buyer_data = {}

    seller = seller_parks[0].seller
    dealer = dealer_parks[0].dealer
    car_model = seller_parks[0]
    seller_history_record_generator(seller, dealer, 20, Decimal(1000.50), car_model)
    dealer_seller_purchase_number_generator(seller, dealer, 20)
    dealer = dealer_parks[1].dealer
    seller_history_record_generator(seller, dealer, 10, Decimal(2000), car_model)
    dealer_seller_purchase_number_generator(seller, dealer, 10)
    predefined_seller_data[seller.pk] = {"sold_cars_number": 30,
                                         "total_revenue": "40010.00",
                                         "avg_sold_car_price": "1333.67",
                                         "uniq_buyers_number": 2,
                                         "most_sold_car": seller_parks[0].car_model.pk}
    seller = seller_parks[1].seller
    dealer = dealer_parks[2].dealer
    car_model_cr = car_park_generator('seller', seller, SellerCarParkModel)
    seller_history_record_generator(seller, dealer, 30, Decimal(1200), car_model_cr)
    car_model = seller_parks[1]
    seller_history_record_generator(seller, dealer, 10, Decimal(1700), car_model)
    dealer_seller_purchase_number_generator(seller, dealer, 40)
    predefined_seller_data[seller.pk] = {"sold_cars_number": 40,
                                         "total_revenue": "53000.00",
                                         "avg_sold_car_price": "1325.00",
                                         "uniq_buyers_number": 1,
                                         "most_sold_car": car_model_cr.car_model.pk}
    seller = seller_parks[2].seller
    predefined_seller_data[seller.pk] = {"sold_cars_number": 0,
                                         "total_revenue": "0.00",
                                         "avg_sold_car_price": "0.00",
                                         "uniq_buyers_number": 0,
                                         "most_sold_car": None}

    def buyer_history_record_generator(dealer: ForeignKey,
                                       buyer: ForeignKey,
                                       bought_quantity: int,
                                       car_price: Decimal,
                                       car_model: DealerCarParkModel):
        """Generates buyer history record"""
        record_data = {
            "bought_car_model": car_model,
            "auto_dealer": dealer,
            "bought_quantity": bought_quantity,
            "car_price": car_price,
            "deal_sum": bought_quantity * car_price,
            "buyer": buyer,
        }
        record = CarBuyerHistoryModel.objects.create(**record_data)
        record.date = date
        record.save()

    def buyer_dealer_purchase_number_generator(dealer: ForeignKey,
                                               buyer: ForeignKey,
                                               purchase_number: int):
        """Generates record with number of buyer from dealer purchases"""
        purchase_number_record = {
            "buyer": buyer,
            "dealer": dealer,
            "purchase_number": purchase_number
        }
        BuyerFromDealerPurchaseNumber.objects.create(**purchase_number_record)

    dealer = dealer_parks[0].dealer
    buyer = buyers[0]
    car_model = dealer_parks[0]
    dealer_history_record_generator(dealer, buyer, 1, Decimal(1500), car_model)
    buyer_history_record_generator(dealer, buyer, 1, Decimal(1500), car_model)
    buyer_dealer_purchase_number_generator(dealer, buyer, 1)
    predefined_buyer_data[buyer.pk] = {"bought_cars_number": 1,
                                       "total_expenses": "1500.00",
                                       "avg_bought_car_price": "1500.00"}
    buyer = buyers[1]
    dealer_history_record_generator(dealer, buyer, 2, Decimal(2000), car_model)
    buyer_history_record_generator(dealer, buyer, 2, Decimal(2000), car_model)
    buyer_dealer_purchase_number_generator(dealer, buyer, 2)
    predefined_dealer_data[dealer.pk] = \
        {"sold_cars_number": 3,
         "total_revenue": "5500.00",
         "avg_sold_car_price": "1833.33",
         "uniq_buyers_number": 2,
         "most_sold_car": car_model.car_model.pk,
         "bought_cars_number": 20,
         "total_expenses": "20010.00",
         "avg_bought_car_price": "1000.50",
         "total_profit": "-14510.00"
         }
    predefined_buyer_data[buyer.pk] = {"bought_cars_number": 2,
                                       "total_expenses": "4000.00",
                                       "avg_bought_car_price": "2000.00"}
    dealer = dealer_parks[1].dealer
    buyer = buyers[2]
    car_model = dealer_parks[0]
    dealer_history_record_generator(dealer, buyer, 1, Decimal(3000), car_model)
    buyer_history_record_generator(dealer, buyer, 1, Decimal(3000), car_model)
    dealer_history_record_generator(dealer, buyer, 1, Decimal(2000), car_model)
    buyer_history_record_generator(dealer, buyer, 1, Decimal(2000), car_model)
    buyer_dealer_purchase_number_generator(dealer, buyer, 2)
    predefined_dealer_data[dealer.pk] = \
        {"sold_cars_number": 2,
         "total_revenue": "5000.00",
         "avg_sold_car_price": "2500.00",
         "uniq_buyers_number": 1,
         "most_sold_car": car_model.car_model.pk,
         "bought_cars_number": 10,
         "total_expenses": "20000.00",
         "avg_bought_car_price": "2000.00",
         "total_profit": "-15000.00"
         }
    predefined_buyer_data[buyer.pk] = {"bought_cars_number": 2,
                                       "total_expenses": "5000.00",
                                       "avg_bought_car_price": "2500.00"}
    dealer = dealer_parks[2].dealer
    predefined_dealer_data[dealer.pk] = \
        {"sold_cars_number": 0,
         "total_revenue": "0.00",
         "avg_sold_car_price": "0.00",
         "uniq_buyers_number": 0,
         "most_sold_car": None,
         "bought_cars_number": 40,
         "total_expenses": "53000.00",
         "avg_bought_car_price": "1325.00",
         "total_profit": "-53000.00"
         }
    return {"predefined_dealer_data": predefined_dealer_data,
            "predefined_seller_data": predefined_seller_data,
            "predefined_buyer_data": predefined_buyer_data}
