from models import MarketAvailableCarModel
from root.common.views import BaseReadOnlyView
from serializers import MarkerAvailableCarsModelSerializer


class MarketAvailableCarModelView(BaseReadOnlyView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel
