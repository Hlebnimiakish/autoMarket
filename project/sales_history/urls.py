from django.urls import path

from .views import (BuyerPurchaseHistoryView, DealerSalesHistoryView,
                    SellerSalesHistoryView)

urlpatterns = [
    path('my_seller_sales_history/',
         SellerSalesHistoryView.as_view(),
         name='seller_sales_history'),
    path('my_dealer_sales_history/',
         DealerSalesHistoryView.as_view(),
         name='dealer_sales_history'),
    path('my_purchase_history/',
         BuyerPurchaseHistoryView.as_view(),
         name='purchase_history'),
]
