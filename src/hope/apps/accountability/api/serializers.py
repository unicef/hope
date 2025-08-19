from django.conf import settings
from rest_framework import serializers

from hope.apps.accountability.models import (
    Feedback,
    FeedbackMessage,
    Message,
    SampleFileExpiredException,
    Survey,
)
from hope.apps.core.api.mixins import AdminUrlSerializerMixin
from hope.apps.geo.api.serializers import AreaSimpleSerializer
from hope.apps.household.api.serializers.household import HouseholdSmallSerializer
from hope.apps.household.models import Household
from hope.apps.payment.api.serializers import (
    FollowUpPaymentPlanSerializer,
    FullListSerializer,
    RandomSamplingSerializer,
)
from hope.apps.payment.models import PaymentPlan
from hope.apps.registration_data.api.serializers import (
    RegistrationDataImportListSerializer,
)
from hope.apps.registration_data.models import RegistrationDataImport


class FeedbackMessageSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackMessage
        fields = (
            "id",
            "description",
            "created_by",
            "created_at",
        )

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class FeedbackMessageCreateSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)


class FeedbackListSerializer(serializers.ModelSerializer):
    household_unicef_id = serializers.CharField(source="household_lookup.unicef_id", allow_null=True)
    household_id = serializers.CharField(source="household_lookup_id", allow_null=True)
    individual_unicef_id = serializers.CharField(source="individual_lookup.unicef_id", allow_null=True)
    individual_id = serializers.CharField(source="individual_lookup_id", allow_null=True)
    linked_grievance_unicef_id = serializers.CharField(source="linked_grievance.unicef_id", allow_null=True)
    linked_grievance_category = serializers.CharField(source="linked_grievance.category", allow_null=True)
    program_name = serializers.CharField(source="program.name", allow_null=True)
    created_by = serializers.SerializerMethodField()
    feedback_messages = FeedbackMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "unicef_id",
            "issue_type",
            "household_unicef_id",
            "household_id",
            "individual_unicef_id",
            "individual_id",
            "linked_grievance_id",
            "linked_grievance_unicef_id",
            "linked_grievance_category",
            "program_name",
            "program_id",
            "created_by",
            "created_at",
            "feedback_messages",
        )

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class FeedbackDetailSerializer(AdminUrlSerializerMixin, FeedbackListSerializer):
    admin2 = AreaSimpleSerializer()

    class Meta(FeedbackListSerializer.Meta):
        fields = FeedbackListSerializer.Meta.fields + (  # type: ignore
            "admin_url",
            "description",
            "area",
            "language",
            "comments",
            "consent",
            "updated_at",
            "admin2",
        )


class FeedbackCreateSerializer(serializers.ModelSerializer):
    issue_type = serializers.ChoiceField(required=True, choices=Feedback.ISSUE_TYPE_CHOICES)
    household_lookup = serializers.UUIDField(allow_null=True, required=False)
    individual_lookup = serializers.UUIDField(allow_null=True, required=False)
    program_id = serializers.UUIDField(allow_null=True, required=False)
    area = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    admin2 = serializers.UUIDField(allow_null=True, required=False)
    description = serializers.CharField()
    language = serializers.CharField(allow_blank=True, required=False)
    comments = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    consent = serializers.BooleanField(default=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "issue_type",
            "household_lookup",
            "individual_lookup",
            "program_id",
            "area",
            "admin2",
            "description",
            "language",
            "comments",
            "consent",
        )


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    issue_type = serializers.ChoiceField(required=True, choices=Feedback.ISSUE_TYPE_CHOICES)
    household_lookup = serializers.UUIDField(allow_null=True, required=False)
    individual_lookup = serializers.UUIDField(allow_null=True, required=False)
    description = serializers.CharField(required=True)
    comments = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    area = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    admin2 = serializers.UUIDField(allow_null=True, required=False)
    language = serializers.CharField(allow_blank=True, required=False)
    consent = serializers.BooleanField(required=False)
    program_id = serializers.UUIDField(allow_null=True, required=False)

    class Meta:
        model = Feedback
        fields = (
            "issue_type",
            "household_lookup",
            "individual_lookup",
            "area",
            "admin2",
            "description",
            "language",
            "comments",
            "consent",
            "program_id",
        )


class MessageListSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "unicef_id",
            "title",
            "number_of_recipients",
            "created_by",
            "created_at",
        )

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


class MessageDetailSerializer(AdminUrlSerializerMixin, MessageListSerializer):
    households = HouseholdSmallSerializer(many=True, read_only=True)
    payment_plan = FollowUpPaymentPlanSerializer(read_only=True)
    registration_data_import = RegistrationDataImportListSerializer(read_only=True)

    class Meta(MessageListSerializer.Meta):
        fields = MessageListSerializer.Meta.fields + (  # type: ignore
            "body",
            "households",
            "payment_plan",
            "registration_data_import",
            "sampling_type",
            "full_list_arguments",
            "random_sampling_arguments",
            "sample_size",
            "admin_url",
        )


class MessageCreateSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()
    sampling_type = serializers.ChoiceField(choices=Message.SamplingChoices)
    full_list_arguments = FullListSerializer(required=False, allow_null=True)
    random_sampling_arguments = RandomSamplingSerializer(required=False, allow_null=True)
    payment_plan = serializers.PrimaryKeyRelatedField(
        queryset=PaymentPlan.objects.all(), required=False, allow_null=True
    )
    registration_data_import = serializers.PrimaryKeyRelatedField(
        queryset=RegistrationDataImport.objects.all(), required=False, allow_null=True
    )
    households = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=Household.objects.all()),
        required=False,
        allow_empty=True,
    )


class AccountabilityFullListArgumentsSerializer(serializers.Serializer):
    excluded_admin_areas = serializers.ListField(child=serializers.CharField(required=True))


class AccountabilityCommunicationMessageAgeInput(serializers.Serializer):
    min = serializers.IntegerField(required=True)
    max = serializers.IntegerField(required=True)


class AccountabilityRandomSamplingArgumentsSerializer(AccountabilityFullListArgumentsSerializer):
    confidence_interval = serializers.FloatField(required=True)
    margin_of_error = serializers.FloatField(required=True)
    age = AccountabilityCommunicationMessageAgeInput(allow_null=True)
    sex = serializers.CharField(allow_null=True)


class SurveySerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    body = serializers.CharField(required=False, allow_blank=True)
    sampling_type = serializers.CharField()
    flow = serializers.CharField(required=False, write_only=True, allow_blank=True)
    payment_plan = serializers.SlugRelatedField(
        slug_field="id",
        required=False,
        allow_null=True,
        queryset=PaymentPlan.objects.all(),
        write_only=True,
    )
    full_list_arguments = AccountabilityFullListArgumentsSerializer(write_only=True, required=False, allow_null=True)
    random_sampling_arguments = AccountabilityRandomSamplingArgumentsSerializer(
        write_only=True, required=False, allow_null=True
    )

    sample_file_path = serializers.SerializerMethodField()
    has_valid_sample_file = serializers.SerializerMethodField()
    rapid_pro_url = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Survey
        fields = (
            "id",
            "unicef_id",
            "title",
            "body",
            "category",
            "sampling_type",
            "flow",
            "flow_id",
            "payment_plan",
            "full_list_arguments",
            "random_sampling_arguments",
            "sample_file_path",
            "has_valid_sample_file",
            "rapid_pro_url",
            "number_of_recipients",
            "created_at",
            "created_by",
        )

    def get_sample_file_path(self, obj: Survey) -> str | None:
        try:
            return obj.sample_file_path()
        except SampleFileExpiredException:
            return None

    def get_has_valid_sample_file(self, obj: Survey) -> bool:
        return obj.has_valid_sample_file()

    def get_rapid_pro_url(self, obj: Survey) -> str | None:
        if not obj.flow_id:
            return None
        return f"{settings.RAPID_PRO_URL}/flow/results/{obj.flow_id}/"

    def get_created_by(self, obj: Feedback) -> str:
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def to_representation(self, obj: Survey) -> dict:
        representation = super().to_representation(obj)
        representation["category"] = obj.get_category_display()
        return representation


class SurveyCategoryChoiceSerializer(serializers.Serializer):
    value: serializers.CharField = serializers.CharField()
    label: serializers.CharField = serializers.CharField()  # type: ignore


class SurveyRapidProFlowSerializer(serializers.Serializer):
    uuid: serializers.CharField = serializers.CharField()
    name: serializers.CharField = serializers.CharField()


class SurveySampleSizeSerializer(serializers.Serializer):
    payment_plan = serializers.PrimaryKeyRelatedField(
        queryset=PaymentPlan.objects.all(), required=False, allow_null=True
    )
    sampling_type = serializers.ChoiceField(required=True, choices=Survey.SAMPLING_CHOICES, allow_null=True)
    full_list_arguments = AccountabilityFullListArgumentsSerializer(required=False, allow_null=True)
    random_sampling_arguments = AccountabilityRandomSamplingArgumentsSerializer(required=False, allow_null=True)


class SampleSizeSerializer(serializers.Serializer):
    number_of_recipients = serializers.IntegerField()
    sample_size = serializers.IntegerField()


class MessageSampleSizeSerializer(serializers.Serializer):
    households = serializers.ListSerializer(
        child=serializers.PrimaryKeyRelatedField(queryset=Household.objects.all()),
        required=False,
        allow_empty=True,
    )
    payment_plan = serializers.PrimaryKeyRelatedField(
        queryset=PaymentPlan.objects.all(), required=False, allow_null=True
    )
    registration_data_import = serializers.PrimaryKeyRelatedField(
        queryset=RegistrationDataImport.objects.all(), required=False, allow_null=True
    )
    sampling_type = serializers.ChoiceField(choices=Message.SamplingChoices)
    full_list_arguments = AccountabilityFullListArgumentsSerializer(required=False, allow_null=True)
    random_sampling_arguments = AccountabilityRandomSamplingArgumentsSerializer(required=False, allow_null=True)
