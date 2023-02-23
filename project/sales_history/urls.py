from rest_framework import routers

from .views import (BuyerPurchaseHistoryOwnView, DealerSalesHistoryOwnView,
                    SellerSalesHistoryOwnView)

history_router = routers.DefaultRouter()
history_router.register('my_seller_sales_history',
                        SellerSalesHistoryOwnView,
                        basename='my-seller-sales-history')
history_router.register('my_dealer_sales_history',
                        DealerSalesHistoryOwnView,
                        basename='my-dealer-sales-history')
history_router.register('my_purchase_history',
                        BuyerPurchaseHistoryOwnView,
                        basename='my-purchase-history')
urlpatterns = history_router.urls
