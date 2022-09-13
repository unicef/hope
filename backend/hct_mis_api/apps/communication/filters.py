from django.db.models.functions import Lower

from django_filters import FilterSet, UUIDFilter

from hct_mis_api.apps.core.utils import CustomOrderingFilter
from hct_mis_api.apps.household.models import Household

from .models import Message


class MessagesFilter(FilterSet):
    class Meta:
        model = Message
        fields = {
            "id": ["exact"],
            "title": ["exact", "icontains", "istartswith"],
            "body": ["icontains", "istartswith"],
            "number_of_recipients": ["exact", "lt", "gt"],
        }

    order_by = CustomOrderingFilter(fields=(Lower("title"),))


class MessageRecipientsMapFilter(FilterSet):
    message_id = UUIDFilter(field_name="messages__id", required=True)
    recipient_id = UUIDFilter(field_name="id")
    full_name = UUIDFilter(field_name="head_of_household__full_name", lookup_expr=["exact", "icontains", "istartswith"])
    phone_no = UUIDFilter(field_name="head_of_household__phone_no", lookup_expr=["exact", "icontains", "istartswith"])

    class Meta:
        model = Household
        fields = []

    order_by = CustomOrderingFilter(
        fields=(
            "residence_status",
            "id",
            Lower("head_of_household__first_name"),
            "size",
            Lower("admin2__name"),
            "residence_status",
            "first_registration_date",
        )
    )
