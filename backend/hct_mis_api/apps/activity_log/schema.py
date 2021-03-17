import graphene
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django_filters import FilterSet, CharFilter
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import DjangoPermissionFilterConnectionField, hopePermissionClass, Permissions
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.utils.schema import Arg


class LogEntryFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    module = CharFilter(
        field_name="content_type__model",
    )

    class Meta:
        model = LogEntry
        fields = ("object_id",)

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            if value.lower() == "system":
                q_obj |= Q(user__isnull=True)
            q_obj |= Q(content_type__model__startswith=value)
            q_obj |= Q(object_id__startswith=value)
            q_obj |= Q(action__startswith=value)
            q_obj |= Q(object_repr__startswith=value)
            q_obj |= Q(user__first_name__startswith=value)
            q_obj |= Q(user__last_name__startswith=value)
            q_obj |= Q(user__email__startswith=value)
            q_obj |= Q(timestamp__startswith=value)
        return qs.filter(q_obj)


class ContentTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = ContentType


class LogEntryNode(DjangoObjectType):
    timestamp = graphene.DateTime()
    changes = Arg()

    class Meta:
        model = LogEntry
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_changes_display_object(self, info):
        return self.changes


class Query(graphene.ObjectType):
    all_log_entries = DjangoPermissionFilterConnectionField(
        LogEntryNode,
        filterset_class=LogEntryFilter,
        permission_classes=(hopePermissionClass(Permissions.ACTIVITY_LOG_VIEW),),
    )
    log_entry_action_choices = graphene.List(ChoiceObject)

    def resolve_log_entry_action_choices(self, info, **kwargs):
        return to_choice_object(LogEntry.LOG_ENTRY_ACTION_CHOICES)
