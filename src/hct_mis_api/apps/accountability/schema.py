import graphene

from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.accountability.filters import (
    MessageRecipientsMapFilter,
    RecipientFilter,
)
from hct_mis_api.apps.accountability.nodes import (
    CommunicationMessageRecipientMapNode,
    RecipientNode,
)


class Query(graphene.ObjectType):
    all_accountability_communication_message_recipients = DjangoPermissionFilterConnectionField(
        CommunicationMessageRecipientMapNode,
        filterset_class=MessageRecipientsMapFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS,
                Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR,
            ),
        ),
    )
    recipients = DjangoPermissionFilterConnectionField(
        RecipientNode,
        filterset_class=RecipientFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS),),
    )
