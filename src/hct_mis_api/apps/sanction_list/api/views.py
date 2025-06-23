from django_filters import rest_framework as filters
from rest_framework import mixins
from rest_framework.filters import OrderingFilter, SearchFilter

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    CountActionMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.sanction_list.api.serializers import (
    SanctionListIndividualSerializer,
)
from hct_mis_api.apps.sanction_list.filters import SanctionListIndividualFilter
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual


class SanctionListIndividualViewSet(
    CountActionMixin,
    SerializerActionMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    BaseViewSet,
):
    queryset = SanctionListIndividual.objects.all()
    serializer_classes_by_action = {
        "list": SanctionListIndividualSerializer,
        "retrieve": SanctionListIndividualSerializer,
    }
    permissions_by_action = {
        "list": [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST, Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        "retrieve": [Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS, Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
    }
    filter_backends = (
        filters.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    filterset_class = SanctionListIndividualFilter
    search_fields = (
        "reference_number",
        "id",
        "full_name",
    )
