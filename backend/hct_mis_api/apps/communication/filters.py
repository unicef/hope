from django.db.models.functions import Lower

from django_filters import CharFilter, FilterSet

from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.household.models import Household

from .models import Message


class MessagesFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)

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
    message_id = CharFilter(method="message_id_filter", required=True)
    recipient_id = CharFilter(method="recipient_id_filter")
    full_name = CharFilter(field_name="head_of_household__full_name", lookup_expr=["exact", "icontains", "istartswith"])
    phone_no = CharFilter(field_name="head_of_household__phone_no", lookup_expr=["exact", "icontains", "istartswith"])

    def message_id_filter(self, queryset, name, value):
        return queryset.filter(message_id=decode_id_string(value))

    def recipient_id_filter(self, queryset, name, value):
        return queryset.filter(id=decode_id_string(value))

    class Meta:
        model = Household
        fields = []

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("head_of_household__first_name"),
            "size",
            Lower("admin2__name"),
            "residence_status",
            "head_of_household__first_registration_date",
        )
    )
