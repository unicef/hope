from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from hope.apps.steficon.api.serializers import RuleSerializer
from hope.apps.steficon.filters import SteficonRuleFilter
from models.steficon import Rule


class RuleEngineViewSet(ListAPIView):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = SteficonRuleFilter
