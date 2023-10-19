from typing import Any, Dict, List, Union

import graphene
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import get_count_and_percentage, to_choice_object
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    UNIQUE,
)
from hct_mis_api.apps.registration_data.filters import RegistrationDataImportFilter
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import UNIQUE_IN_BATCH


class CountAndPercentageNode(graphene.ObjectType):
    count = graphene.Int()
    percentage = graphene.Float()


class RegistrationDataImportNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.RDI_VIEW_DETAILS),)

    batch_duplicates_count_and_percentage = graphene.Field(CountAndPercentageNode)
    golden_record_duplicates_count_and_percentage = graphene.Field(CountAndPercentageNode)
    batch_possible_duplicates_count_and_percentage = graphene.Field(CountAndPercentageNode)
    golden_record_possible_duplicates_count_and_percentage = graphene.Field(CountAndPercentageNode)
    batch_unique_count_and_percentage = graphene.Field(CountAndPercentageNode)
    golden_record_unique_count_and_percentage = graphene.Field(CountAndPercentageNode)
    total_households_count_with_valid_phone_no = graphene.Int()

    class Meta:
        model = RegistrationDataImport
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    def resolve_batch_duplicates_count_and_percentage(root, info: Any, **kwargs: Any) -> Dict[str, Union[int, float]]:
        batch_duplicates = root.all_imported_individuals.filter(deduplication_batch_status=DUPLICATE_IN_BATCH)
        return get_count_and_percentage(batch_duplicates, root.all_imported_individuals)

    def resolve_golden_record_duplicates_count_and_percentage(
        root, info: Any, **kwargs: Any
    ) -> Dict[str, Union[int, float]]:
        gr_duplicates = root.all_imported_individuals.filter(deduplication_golden_record_status=DUPLICATE)
        return get_count_and_percentage(gr_duplicates, root.all_imported_individuals)

    def resolve_golden_record_possible_duplicates_count_and_percentage(
        root, info: Any, **kwargs: Any
    ) -> Dict[str, Union[int, float]]:
        gr_similar = root.all_imported_individuals.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        return get_count_and_percentage(gr_similar, root.all_imported_individuals)

    def resolve_batch_unique_count_and_percentage(root, info: Any, **kwargs: Any) -> Dict[str, Union[int, float]]:
        unique = root.all_imported_individuals.filter(deduplication_batch_status=UNIQUE_IN_BATCH)
        return get_count_and_percentage(unique, root.all_imported_individuals)

    def resolve_golden_record_unique_count_and_percentage(
        root, info: Any, **kwargs: Any
    ) -> Dict[str, Union[int, float]]:
        unique = root.all_imported_individuals.filter(deduplication_golden_record_status=UNIQUE)
        return get_count_and_percentage(unique, root.all_imported_individuals)

    def resolve_total_households_count_with_valid_phone_no(self, info: Any) -> int:
        return self.households.exclude(
            head_of_household__phone_no_valid=False,
            head_of_household__phone_no_alternative_valid=False,
        ).count()


class Query(graphene.ObjectType):
    registration_data_import = graphene.relay.Node.Field(
        RegistrationDataImportNode,
    )
    all_registration_data_imports = DjangoPermissionFilterConnectionField(
        RegistrationDataImportNode,
        filterset_class=RegistrationDataImportFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.RDI_VIEW_LIST, *ALL_GRIEVANCES_CREATE_MODIFY),),
    )
    registration_data_status_choices = graphene.List(ChoiceObject)

    def resolve_registration_data_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(RegistrationDataImport.STATUS_CHOICE)
