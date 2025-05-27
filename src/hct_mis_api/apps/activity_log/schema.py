from typing import Any, Dict, List, Optional

import graphene
from django.contrib.contenttypes.models import ContentType
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField, Permissions, hopePermissionClass)
from hct_mis_api.apps.activity_log.filters import LogEntryFilter
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.utils.schema import Arg


class ContentTypeObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = ContentType


class LogEntryNode(DjangoObjectType):
    timestamp = graphene.DateTime()
    changes = Arg()
    is_user_generated = graphene.Boolean()

    class Meta:
        model = LogEntry
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_changes_display_object(self, info: Any) -> Arg:
        return self.changes

    def resolve_is_user_generated(self, info: Any) -> Optional[bool]:
        from hct_mis_api.apps.grievance.models import GrievanceTicket

        if isinstance(self.content_object, GrievanceTicket):
            return self.content_object.grievance_type_to_string() == "user"
        return None


class Query(graphene.ObjectType):
    all_log_entries = DjangoPermissionFilterConnectionField(
        LogEntryNode,
        filterset_class=LogEntryFilter,
        permission_classes=(hopePermissionClass(Permissions.ACTIVITY_LOG_VIEW),),
    )
    log_entry_action_choices = graphene.List(ChoiceObject)

    def resolve_log_entry_action_choices(self, info: Any) -> List[Dict[str, Any]]:
        return to_choice_object(LogEntry.LOG_ENTRY_ACTION_CHOICES)
