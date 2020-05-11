import graphene
from django_filters import FilterSet, OrderingFilter, DateFilter, CharFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ChoiceObject
from core.extended_connection import ExtendedConnection
from registration_data.models import RegistrationDataImport


class RegistrationDataImportFilter(FilterSet):
    import_date = DateFilter(field_name="import_date__date")
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        model = RegistrationDataImport
        fields = {
            "imported_by__id": ["exact"],
            "import_date": ["exact"],
            "status": ["exact"],
            "name": ["exact", "icontains"],
            "business_area": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            "name",
            "status",
            "import_date",
            "number_of_households",
            "imported_by__given_name",
        )
    )


class RegistrationDataImportNode(DjangoObjectType):
    class Meta:
        model = RegistrationDataImport
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    registration_data_import = graphene.relay.Node.Field(
        RegistrationDataImportNode,
    )
    all_registration_data_imports = DjangoFilterConnectionField(
        RegistrationDataImportNode,
        filterset_class=RegistrationDataImportFilter,
    )
    registration_data_status_choices = graphene.List(ChoiceObject)

    def resolve_registration_data_status_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in RegistrationDataImport.STATUS_CHOICE
        ]
