from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hct_mis_api.apps.steficon.api.serializers import RuleSerializer
from hct_mis_api.apps.steficon.filters import SteficonRuleFilter
from hct_mis_api.apps.steficon.models import Rule


class RuleEngineViewSet(ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = SteficonRuleFilter
