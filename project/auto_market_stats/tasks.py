# pylint: skip-file

"""This module contains tasks for dealer, seller and buyer statistics calculation"""

import datetime
from decimal import Decimal
from typing import Type

from car_market.models import MarketAvailableCarModel
from car_park.models import DealerCarParkModel, SellerCarParkModel
from celery import shared_task
from django.db.models import QuerySet, Sum
from sales_history.models import (BaseSalesHistoryModel, CarBuyerHistoryModel,
                                  DealerSalesHistoryModel,
                                  SellerSalesHistoryModel)
from user.models import (AutoDealerModel, AutoSellerModel,
                         BuyerFromDealerPurchaseNumber, CarBuyerModel,
                         DealerFromSellerPurchaseNumber)

from .models import (OverallBuyerStatisticsModel, OverallDealerStatisticsModel,
                     OverallSellerStatisticsModel)


def history_records_statistics_calculator(history_records:
                                          QuerySet[BaseSalesHistoryModel]) \
        -> dict[str, int | Decimal]:
    """Calculates number of sold cars and revenue from given history records,
    returns dictionary with calculated data"""
    values_dict = history_records.aggregate(sold_cars_number=Sum('sold_cars_quantity'),
                                            revenue=Sum('deal_sum'))
    return values_dict


def additional_history_stats_calculator(history_records:
                                        QuerySet[BaseSalesHistoryModel |
                                                 CarBuyerHistoryModel],
                                        user_type: str) -> dict[str, int | Decimal]:
    """Calculates number of bought cars and expenses from given history records,
    returns dictionary with calculated data"""
    if user_type == "buyer":
        values_dict = history_records.aggregate(bought_cars_number=Sum('bought_quantity'),
                                                expenses=Sum('deal_sum'))
    else:
        values_dict = history_records.aggregate(bought_cars_number=Sum('sold_cars_quantity'),
                                                expenses=Sum('deal_sum'))
    return values_dict


def most_sold_cars_finder(filter_param: str,
                          user_profile: AutoSellerModel | AutoDealerModel,
                          history_records_model_type:
                          Type[SellerSalesHistoryModel | DealerSalesHistoryModel]) \
        -> None | MarketAvailableCarModel:
    """Takes in parameter to filter history records, user profile model, type of history
    records model and calculates the most sold cars model from all history records, returns
    market available car model of the most sold car or None if no records were found"""
    most_sold_car_model = None
    history_records = history_records_model_type.objects.filter(**{filter_param: user_profile})
    sold_cars = \
        history_records.values("sold_car_model").\
        annotate(sold_quantity=Sum('sold_cars_quantity')).\
        order_by('-sold_quantity')
    if sold_cars:
        most_sold_car = sold_cars[0]['sold_car_model']
        most_sold_car_model = SellerCarParkModel.objects.get(id=most_sold_car).car_model
        if filter_param == 'dealer':
            most_sold_car_model = DealerCarParkModel.objects.get(id=most_sold_car).car_model
    return most_sold_car_model


def history_records_collector(date: datetime.date,
                              created: bool,
                              user_history_model_type:
                              Type[BaseSalesHistoryModel |
                                   CarBuyerHistoryModel],
                              filter_param: str,
                              user_profile:
                              AutoDealerModel |
                              AutoSellerModel |
                              CarBuyerModel,
                              stats_model:
                              OverallSellerStatisticsModel |
                              OverallDealerStatisticsModel |
                              OverallBuyerStatisticsModel) \
        -> QuerySet[BaseSalesHistoryModel | CarBuyerHistoryModel] | None:
    """Search for history records to be calculated from the given parameters, considering last
    already analyzed date and current date given, returns history records queryset to be analyzed
    or None if all available records were analyzed"""
    history_records = None
    if created:
        history_records = user_history_model_type.objects.filter(date__lte=date,
                                                                 **{filter_param: user_profile})
    elif stats_model.last_analyzed_date and date > stats_model.last_analyzed_date:
        history_records = \
            user_history_model_type.objects.filter(date__gt=stats_model.last_analyzed_date,
                                                   date__lte=date,
                                                   **{filter_param: user_profile})
    return history_records


def gather_seller_or_dealer_base_statistics(date: datetime.date,
                                            filter_param: str,
                                            created: bool,
                                            stats_model:
                                            OverallSellerStatisticsModel |
                                            OverallDealerStatisticsModel,
                                            user_history_model_type:
                                            Type[SellerSalesHistoryModel |
                                                 DealerSalesHistoryModel],
                                            user_profile:
                                            AutoDealerModel | AutoSellerModel,
                                            purchase_number_model:
                                            Type[DealerFromSellerPurchaseNumber |
                                                 BuyerFromDealerPurchaseNumber]):
    """Collects and calculates base dealer or seller statistics, and adds collected data to
    corresponding statistics model"""
    history_records = history_records_collector(date,
                                                created,
                                                user_history_model_type,
                                                filter_param,
                                                user_profile,
                                                stats_model)
    if history_records:
        history_records_stats = history_records_statistics_calculator(history_records)
        sold_cars_number = \
            int(stats_model.sold_cars_number) + history_records_stats['sold_cars_number']
        total_revenue = \
            Decimal(stats_model.total_revenue) + history_records_stats['revenue']
        avg_sold_car_price = 0
        if sold_cars_number:
            avg_sold_car_price = total_revenue / sold_cars_number
        most_sold_car = most_sold_cars_finder(filter_param,
                                              user_profile,
                                              user_history_model_type)
        uniq_buyers_number = \
            purchase_number_model.objects.filter(**{filter_param: user_profile}).count()
        stats_model.sold_cars_number = sold_cars_number
        stats_model.total_revenue = total_revenue
        stats_model.avg_sold_car_price = avg_sold_car_price
        stats_model.most_sold_car = most_sold_car
        stats_model.uniq_buyers_number = uniq_buyers_number
        stats_model.save()


def gather_additional_statistics(date: datetime.date,
                                 created: bool,
                                 filter_param: str,
                                 stats_model:
                                 OverallDealerStatisticsModel | OverallBuyerStatisticsModel,
                                 user_profile: AutoDealerModel,
                                 user_history_model_type:
                                 Type[SellerSalesHistoryModel | CarBuyerHistoryModel],
                                 user_type: str):
    """Collects and calculates additional statistics about purchases, and adds collected data to
    corresponding statistics model"""
    history_records = history_records_collector(date,
                                                created,
                                                user_history_model_type,
                                                filter_param,
                                                user_profile,
                                                stats_model)
    if history_records:
        history_records_stats = additional_history_stats_calculator(history_records, user_type)
        bought_cars_number = \
            int(stats_model.bought_cars_number) + history_records_stats['bought_cars_number']
        total_expenses = \
            Decimal(stats_model.total_expenses) + history_records_stats['expenses']
        avg_bought_car_price = 0
        if bought_cars_number:
            avg_bought_car_price = total_expenses / bought_cars_number
        stats_model.bought_cars_number = bought_cars_number
        stats_model.total_expenses = total_expenses
        stats_model.avg_bought_car_price = avg_bought_car_price
        stats_model.save()


@shared_task(name='seller_stats')
def get_seller_statistics():
    """Celery task to be run at night, which calculates and saves to seller statistics
    models new statistics data"""
    date = datetime.date.today() - datetime.timedelta(days=1)
    for seller in AutoSellerModel.objects.all():
        seller_stats = \
            OverallSellerStatisticsModel.objects.get_or_create(seller=seller)
        seller_stats_model = seller_stats[0]
        gather_seller_or_dealer_base_statistics(date,
                                                'seller',
                                                seller_stats[1],
                                                seller_stats_model,
                                                SellerSalesHistoryModel,
                                                seller,
                                                DealerFromSellerPurchaseNumber)
        seller_stats_model.last_analyzed_date = date
        seller_stats_model.save()


@shared_task(name='dealer_stats')
def get_dealer_statistics():
    """Celery task to be run at night, which calculates and saves to dealer statistics
    models new statistics data"""
    date = datetime.date.today() - datetime.timedelta(days=1)
    for dealer in AutoDealerModel.objects.all():
        dealer_stats = \
            OverallDealerStatisticsModel.objects.get_or_create(dealer=dealer)
        dealer_stats_model = dealer_stats[0]
        gather_seller_or_dealer_base_statistics(date,
                                                'dealer',
                                                dealer_stats[1],
                                                dealer_stats_model,
                                                DealerSalesHistoryModel,
                                                dealer,
                                                BuyerFromDealerPurchaseNumber)
        gather_additional_statistics(date,
                                     dealer_stats[1],
                                     'car_buyer',
                                     dealer_stats_model,
                                     dealer,
                                     SellerSalesHistoryModel,
                                     'dealer')
        dealer_stats_model.total_profit = \
            Decimal(dealer_stats_model.total_revenue) - \
            Decimal(dealer_stats_model.total_expenses)
        dealer_stats_model.last_analyzed_date = date
        dealer_stats_model.save()


@shared_task(name='buyer_stats')
def get_buyer_statistics():
    """Celery task to be run at night, which calculates and saves to buyer statistics
    models new statistics data"""
    date = datetime.date.today() - datetime.timedelta(days=1)
    for buyer in CarBuyerModel.objects.all():
        buyer_stats = \
            OverallBuyerStatisticsModel.objects.get_or_create(buyer=buyer)
        buyer_stats_model = buyer_stats[0]
        gather_additional_statistics(date,
                                     buyer_stats[1],
                                     'buyer',
                                     buyer_stats_model,
                                     buyer,
                                     CarBuyerHistoryModel,
                                     'buyer')
        buyer_stats_model.last_analyzed_date = date
        buyer_stats_model.save()
