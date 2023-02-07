from root.common.views import BaseReadOnlyView

from .models import MarketAvailableCarModel
from .serializers import MarkerAvailableCarsModelSerializer


class MarketAvailableCarModelView(BaseReadOnlyView):
    serializer = MarkerAvailableCarsModelSerializer
    model = MarketAvailableCarModel
