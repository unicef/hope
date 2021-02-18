import graphene
from django.db.models.functions import Lower
from django_filters import FilterSet, DateFilter, CharFilter
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField,
    hopePermissionClass,
    Permissions,
    BaseNodePermissionMixin,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import get_count_and_percentage, CustomOrderingFilter
from hct_mis_api.apps.household.models import DUPLICATE, NEEDS_ADJUDICATION, UNIQUE, DUPLICATE_IN_BATCH
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import UNIQUE_IN_BATCH


class RegistrationDataImportFilter(FilterSet):
    import_date = DateFilter(field_name="import_date__date")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        model = RegistrationDataImport
        fields = {
            "imported_by__id": ["exact"],
            "import_date": ["exact"],
            "status": ["exact"],
            "name": ["exact", "startswith"],
            "business_area": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(
            Lower("name"),
            "status",
            "import_date",
            "number_of_individuals",
            "number_of_households",
            "data_source",
            Lower("imported_by__first_name"),
        )
    )


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

    class Meta:
        model = RegistrationDataImport
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    def resolve_batch_duplicates_count_and_percentage(root, info, **kwargs):
        batch_duplicates = root.all_imported_individuals.filter(deduplication_batch_status=DUPLICATE_IN_BATCH)
        return get_count_and_percentage(batch_duplicates, root.all_imported_individuals)

    def resolve_golden_record_duplicates_count_and_percentage(root, info, **kwargs):
        gr_duplicates = root.all_imported_individuals.filter(deduplication_golden_record_status=DUPLICATE)
        return get_count_and_percentage(gr_duplicates, root.all_imported_individuals)

    # def resolve_batch_possible_duplicates_count_and_percentage(root, info, **kwargs):
    #     batch_similar = root.all_imported_individuals.filter(deduplication_batch_status=SIMILAR_IN_BATCH)
    #     return get_count_and_percentage(batch_similar, root.all_imported_individuals)

    def resolve_golden_record_possible_duplicates_count_and_percentage(root, info, **kwargs):
        gr_similar = root.all_imported_individuals.filter(deduplication_golden_record_status=NEEDS_ADJUDICATION)
        return get_count_and_percentage(gr_similar, root.all_imported_individuals)

    def resolve_batch_unique_count_and_percentage(root, info, **kwargs):
        unique = root.all_imported_individuals.filter(deduplication_batch_status=UNIQUE_IN_BATCH)
        return get_count_and_percentage(unique, root.all_imported_individuals)

    def resolve_golden_record_unique_count_and_percentage(root, info, **kwargs):
        unique = root.all_imported_individuals.filter(deduplication_golden_record_status=UNIQUE)
        return get_count_and_percentage(unique, root.all_imported_individuals)


class Query(graphene.ObjectType):
    registration_data_import = graphene.relay.Node.Field(
        RegistrationDataImportNode,
    )
    all_registration_data_imports = DjangoPermissionFilterConnectionField(
        RegistrationDataImportNode,
        filterset_class=RegistrationDataImportFilter,
        permission_classes=(hopePermissionClass(Permissions.RDI_VIEW_LIST),),
    )
    registration_data_status_choices = graphene.List(ChoiceObject)

    def resolve_registration_data_status_choices(self, info, **kwargs):
        return [{"name": name, "value": value} for value, name in RegistrationDataImport.STATUS_CHOICE]
