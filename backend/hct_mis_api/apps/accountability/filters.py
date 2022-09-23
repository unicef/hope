from django.db.models.functions import Lower

from django_filters import CharFilter, ChoiceFilter, FilterSet

from hct_mis_api.apps.core.filters import DateTimeRangeFilter
from hct_mis_api.apps.core.utils import CustomOrderingFilter, decode_id_string
from hct_mis_api.apps.household.models import Household

from .models import Feedback, Message


class MessagesFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    program = CharFilter(method="filter_program")
    created_at_range = DateTimeRangeFilter(field_name="created_at")
    title = CharFilter(field_name="title", lookup_expr="icontains")
    body = CharFilter(field_name="body", lookup_expr="icontains")
    sampling_type = ChoiceFilter(field_name="sampling_type", choices=Message.SamplingChoices.choices)
    created_by = CharFilter(method="filter_created_by")

    def filter_program(self, queryset, name, value):
        return queryset.filter(target_population__program=decode_id_string(value))

    def filter_created_by(self, queryset, name, value):
        return queryset.filter(created_by_id=decode_id_string(value))

    class Meta:
        model = Message
        fields = {
            "number_of_recipients": ["exact", "gte", "lte"],
            "target_population": ["exact"],
            "created_by": ["exact"],
        }

    order_by = CustomOrderingFilter(fields=(Lower("title"), "number_of_recipients", "sampling_type"))


class MessageRecipientsMapFilter(FilterSet):
    message_id = CharFilter(method="filter_message_id", required=True)
    recipient_id = CharFilter(method="filter_recipient_id")
    full_name = CharFilter(field_name="head_of_household__full_name", lookup_expr=["exact", "icontains", "istartswith"])
    phone_no = CharFilter(field_name="head_of_household__phone_no", lookup_expr=["exact", "icontains", "istartswith"])
    sex = CharFilter(field_name="head_of_household__sex")

    def filter_message_id(self, queryset, name, value):
        return queryset.filter(messages__id=decode_id_string(value))

    def filter_recipient_id(self, queryset, name, value):
        return queryset.filter(head_of_household_id=decode_id_string(value))

    class Meta:
        model = Household
        fields = []

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            Lower("head_of_household__first_name"),
            Lower("head_of_household__sex"),
            "size",
            Lower("admin2__name"),
            "residence_status",
            "head_of_household__first_registration_date",
        )
    )


class FeedbackFilter(FilterSet):
    business_area_slug = CharFilter(field_name="business_area__slug", required=True)

    class Meta:
        model = Feedback
        fields = []
