import re
from typing import Any, Dict, Optional

from django.db.models import Q, Value
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.account.api.serializers import PartnerForProgramSerializer
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.api.serializers import DataCollectingTypeSerializer
from hct_mis_api.apps.core.models import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from hct_mis_api.apps.core.utils import check_concurrency_version_in_mutation
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.periodic_data_update.api.serializers import (
    PeriodicFieldSerializer,
)
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle


def validate_cycle_timeframes_overlapping(
    program: Program,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_cycle_id: Optional[str] = None,
) -> None:
    cycle_qs = program.cycles.exclude(id=current_cycle_id)
    if start_date:
        if cycle_qs.filter(Q(start_date__lte=start_date) & Q(end_date__gte=start_date)).exists():
            raise serializers.ValidationError(
                {"start_date": "Programme Cycles' timeframes must not overlap with the provided start date."}
            )
    if end_date:
        if cycle_qs.filter(Q(start_date__lte=end_date) & Q(end_date__gte=end_date)).exists():
            raise serializers.ValidationError(
                {"end_date": "Programme Cycles' timeframes must not overlap with the provided end date."}
            )
    if start_date and end_date:
        if cycle_qs.filter(
            Q(start_date__lte=start_date) & Q(end_date__gte=end_date)
            | Q(start_date__gte=start_date) & Q(end_date__lte=end_date)
            | Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
        ).exists():
            raise serializers.ValidationError("Programme Cycles' timeframes must not overlap with the provided dates.")


def validate_programme_code(programme_code: str) -> str:
    programme_code = programme_code.upper()
    if not re.match(r"^[A-Z0-9\-]{4}$", programme_code):
        raise serializers.ValidationError(
            "Programme code should be exactly 4 characters long and may only contain letters, digits "
            "and character: -"
        )
    return programme_code


def validate_data_collecting_type(data_collecting_type: DataCollectingType, business_area_slug: str) -> None:
    # validate DCT.limit_to
    if (
        data_collecting_type.limit_to.exists()
        and not data_collecting_type.limit_to.filter(slug=business_area_slug).exists()
    ):
        raise serializers.ValidationError("This Data Collecting Type is not available for this Business Area.")

    # validate DCT
    if not data_collecting_type.active:
        raise serializers.ValidationError("Only active Data Collecting Type can be used in Program.")
    elif data_collecting_type.deprecated:
        raise serializers.ValidationError("Deprecated Data Collecting Type cannot be used in Program.")


def validate_data_collecting_type_and_beneficiary_group_combination(
    data_collecting_type: DataCollectingType, beneficiary_group: BeneficiaryGroup
) -> None:
    if (data_collecting_type.type == DataCollectingType.Type.SOCIAL and beneficiary_group.master_detail) or (
        data_collecting_type.type == DataCollectingType.Type.STANDARD and not beneficiary_group.master_detail
    ):
        raise serializers.ValidationError(
            {"beneficiary_group": "Selected combination of data collecting type and beneficiary group is invalid."}
        )


def validate_partners_data(partners: list[Dict[str, Any]], partner_access: str, user_partner: Partner) -> None:
    partners_ids = [int(partner["partner"]) for partner in partners]
    if (
        partner_access == Program.SELECTED_PARTNERS_ACCESS
        and not user_partner.is_unicef_subpartner
        and user_partner.id not in partners_ids
    ):
        raise serializers.ValidationError(
            {"partners": "Please assign access to your partner before saving the Program."}
        )
    if partners_ids and partner_access != Program.SELECTED_PARTNERS_ACCESS:
        raise serializers.ValidationError({"partners": "You cannot specify partners for the chosen access type."})


def validate_end_date_after_start_date(start_date: str, end_date: str) -> None:
    if end_date < start_date:
        raise serializers.ValidationError({"end_date": "End date cannot be earlier than the start date."})


class ProgramCycleListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    created_by = serializers.SerializerMethodField()
    start_date = serializers.DateField(format="%Y-%m-%d")
    end_date = serializers.DateField(format="%Y-%m-%d")
    program_start_date = serializers.DateField(format="%Y-%m-%d")
    program_end_date = serializers.DateField(format="%Y-%m-%d")
    admin_url = serializers.SerializerMethodField()
    can_remove_cycle = serializers.SerializerMethodField()

    class Meta:
        model = ProgramCycle
        fields = (
            "id",
            "title",
            "status",
            "start_date",
            "end_date",
            "program_start_date",
            "program_end_date",
            "created_at",
            "total_entitled_quantity_usd",
            "total_undelivered_quantity_usd",
            "total_delivered_quantity_usd",
            "frequency_of_payments",
            "created_by",
            "admin_url",
            "can_remove_cycle",
        )

    def get_created_by(self, obj: ProgramCycle) -> str:
        if not obj.created_by:
            return "-"
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"

    def get_admin_url(self, obj: ProgramCycle) -> Optional[str]:
        user = self.context["request"].user
        return obj.admin_url if user.is_superuser else None

    def get_can_remove_cycle(self, obj: ProgramCycle) -> bool:
        return obj.can_remove_cycle


class ProgramCycleCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False)

    class Meta:
        model = ProgramCycle
        fields = ["title", "start_date", "end_date"]

    def get_program(self) -> Program:
        request = self.context["request"]
        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
        program_slug = request.parser_context["kwargs"]["program_slug"]
        program = get_object_or_404(Program, business_area__slug=business_area_slug, slug=program_slug)
        return program

    def validate_title(self, value: str) -> str:
        program = self.get_program()
        cycles = program.cycles.all()
        if cycles.filter(title=value).exists():
            raise serializers.ValidationError("Programme Cycle title should be unique.")
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context["request"]
        program = self.get_program()
        start_date = data["start_date"]
        end_date = data.get("end_date")
        data["program"] = program
        data["created_by"] = request.user

        # Validation: Program must be ACTIVE
        if program.status != Program.ACTIVE:
            raise serializers.ValidationError("Programme Cycle can only be created for an Active Programme.")

        if program.end_date:
            if not (program.start_date <= start_date <= program.end_date):
                raise serializers.ValidationError(
                    {"start_date": "Programme Cycle start date must be between programme start and end dates."}
                )
        else:
            if start_date < program.start_date:
                raise serializers.ValidationError(
                    {"start_date": "Programme Cycle start date cannot be before programme start date."}
                )

        if end_date:
            if not program.end_date and end_date < program.start_date:
                raise serializers.ValidationError(
                    {"end_date": "Programme Cycle end date cannot be before programme start date."}
                )

            if end_date < start_date:
                raise serializers.ValidationError({"end_date": "End date cannot be before start date."})

            if program.end_date and not (program.start_date <= end_date <= program.end_date):
                raise serializers.ValidationError(
                    {"end_date": "Programme Cycle end date must be between programme start and end dates."}
                )

        if program.cycles.filter(end_date__isnull=True).exists():
            raise serializers.ValidationError("All Programme Cycles must have an end date before creating a new one.")

        if program.cycles.filter(end_date__gte=start_date).exists():
            raise serializers.ValidationError({"start_date": "Start date must be after the latest cycle end date."})
        return data


class ProgramCycleUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    class Meta:
        model = ProgramCycle
        fields = ["title", "start_date", "end_date"]

    def validate_title(self, value: str) -> str:
        if (
            ProgramCycle.objects.filter(title=value, program=self.instance.program)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise serializers.ValidationError("Programme Cycle with this title already exists.")

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        program = self.instance.program
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        program_start_date = (
            parse_date(program.start_date) if isinstance(program.start_date, str) else program.start_date
        )
        # program end date can be empty
        program_end_date = (
            (parse_date(program.end_date) if isinstance(program.end_date, str) else program.end_date)
            if program.end_date
            else None
        )

        if program.status != Program.ACTIVE:
            raise serializers.ValidationError("Updating Programme Cycle is only possible for Active Programme.")

        if self.instance.end_date and "end_date" in data and end_date is None:
            raise serializers.ValidationError(
                {"end_date": "Cannot clear the Programme Cycle end date if it was previously set."}
            )

        if start_date:
            if program_end_date:
                if not (program_start_date <= start_date <= program_end_date):
                    raise serializers.ValidationError(
                        {"start_date": "Programme Cycle start date must be within the programme's start and end dates."}
                    )
            elif start_date < program_start_date:
                raise serializers.ValidationError(
                    {"start_date": "Programme Cycle start date must be after the programme start date."}
                )

        if end_date:
            if program_end_date:
                if not (program_start_date <= end_date <= program_end_date):
                    raise serializers.ValidationError(
                        {"end_date": "Programme Cycle end date must be within the programme's start and end dates."}
                    )

            if start_date and end_date < start_date:
                raise serializers.ValidationError({"end_date": "End date cannot be earlier than the start date."})

        validate_cycle_timeframes_overlapping(program, start_date, end_date, str(self.instance.pk))
        return data


class BeneficiaryGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeneficiaryGroup
        fields = (
            "id",
            "name",
            "group_label",
            "group_label_plural",
            "member_label",
            "member_label_plural",
            "master_detail",
        )


class ProgramListSerializer(serializers.ModelSerializer):
    data_collecting_type = DataCollectingTypeSerializer()
    pdu_fields = serializers.SerializerMethodField()
    beneficiary_group = BeneficiaryGroupSerializer()

    class Meta:
        model = Program
        fields = (
            "id",
            "programme_code",
            "slug",
            "name",
            "start_date",
            "end_date",
            "budget",
            "frequency_of_payments",
            "sector",
            "cash_plus",
            "population_goal",
            "data_collecting_type",
            "beneficiary_group",
            "status",
            "pdu_fields",
            "household_count",
        )
        extra_kwargs = {"status": {"help_text": "Status"}}  # for swagger purpose

    def get_pdu_fields(self, obj: Program) -> list[str]:
        return [pdu_field.id for pdu_field in obj.pdu_fields.all()]  # to save queries


class ProgramDetailSerializer(AdminUrlSerializerMixin, ProgramListSerializer):
    partners = serializers.SerializerMethodField()
    registration_imports_total_count = serializers.SerializerMethodField()
    target_populations_count = serializers.SerializerMethodField()

    class Meta(ProgramListSerializer.Meta):
        fields = ProgramListSerializer.Meta.fields + (  # type: ignore
            "admin_url",
            "description",
            "administrative_areas_of_implementation",
            "version",
            "partners",
            "partner_access",
            "registration_imports_total_count",
            "target_populations_count",
            "population_goal",
            "version",
        )

    def get_registration_imports_total_count(self, obj: Program) -> int:
        return obj.registration_imports.count() if hasattr(obj, "registration_imports") else 0

    def get_target_populations_count(self, obj: Program) -> int:
        return PaymentPlan.objects.filter(program_cycle__program=obj).count()

    def get_partners(self, obj: Program) -> ReturnDict:
        partners_qs = (
            Partner.objects.filter(
                Q(role_assignments__program=obj)
                | (Q(role_assignments__program=None) & Q(role_assignments__business_area=obj.business_area))
            )
            .annotate(partner_program=Value(obj.id))
            .order_by("name")
            .distinct()
        )
        return PartnerForProgramSerializer(partners_qs, many=True).data


class PartnersDataSerializer(serializers.Serializer):
    partner = serializers.CharField()
    areas = serializers.ListField(child=serializers.CharField())


class PDUDataSerializer(serializers.Serializer):
    subtype = serializers.ChoiceField(choices=PeriodicFieldData.TYPE_CHOICES)
    number_of_rounds = serializers.IntegerField(min_value=1)
    rounds_names = serializers.ListField(child=serializers.CharField(max_length=100, allow_blank=True))


class PDUFieldsCreateSerializer(serializers.Serializer):
    label = serializers.CharField()  # type: ignore
    pdu_data = PDUDataSerializer()


class PDUFieldsUpdateSerializer(PDUFieldsCreateSerializer):
    id = serializers.CharField(required=False)


class ProgramCreateSerializer(serializers.ModelSerializer):
    programme_code = serializers.CharField(min_length=4, max_length=4, allow_null=True, required=False)
    data_collecting_type = serializers.SlugRelatedField(slug_field="code", queryset=DataCollectingType.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField(allow_null=True)
    partners = PartnersDataSerializer(many=True)
    pdu_fields = PDUFieldsCreateSerializer(many=True)
    slug = serializers.CharField(read_only=True)
    version = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Program
        fields = (
            "id",
            "programme_code",
            "name",
            "slug",
            "sector",
            "description",
            "budget",
            "administrative_areas_of_implementation",
            "population_goal",
            "cash_plus",
            "frequency_of_payments",
            "data_collecting_type",
            "beneficiary_group",
            "start_date",
            "end_date",
            "pdu_fields",
            "partners",
            "partner_access",
            "version",
            "status",
        )

    def validate_programme_code(self, value: Optional[str]) -> Optional[str]:
        if value:
            value = validate_programme_code(value)
            business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
            if Program.objects.filter(business_area__slug=business_area_slug, programme_code=value).exists():
                raise serializers.ValidationError("Programme code is already used.")
        return value

    def validate_data_collecting_type(self, value: DataCollectingType) -> DataCollectingType:
        data_collecting_type = value
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        validate_data_collecting_type(data_collecting_type, business_area_slug)
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # validate start_date and end_date
        end_date = data.get("end_date")
        if end_date:
            validate_end_date_after_start_date(data["start_date"], end_date)

        # validate partners and partner_access
        partners = data.get("partners", [])
        partner_access = data["partner_access"]
        partner = self.context["request"].user.partner
        validate_partners_data(partners, partner_access, partner)

        # validate DCT and BG combination
        data_collecting_type = data["data_collecting_type"]
        beneficiary_group = data["beneficiary_group"]
        validate_data_collecting_type_and_beneficiary_group_combination(data_collecting_type, beneficiary_group)
        return data

    def to_representation(self, obj: Program) -> Dict:
        """
        Override to_representation to include the partners and pdu_fields in the correct format.
        """
        representation = super().to_representation(obj)
        partners_qs = (
            Partner.objects.filter(
                Q(role_assignments__program=obj)
                | (Q(role_assignments__program=None) & Q(role_assignments__business_area=obj.business_area))
            )
            .annotate(partner_program=Value(obj.id))
            .order_by("name")
            .distinct()
        )
        representation["partners"] = PartnerForProgramSerializer(partners_qs, many=True).data
        representation["pdu_fields"] = PeriodicFieldSerializer(
            FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=obj).order_by("name"), many=True
        ).data
        return representation


class ProgramUpdateSerializer(serializers.ModelSerializer):
    programme_code = serializers.CharField(min_length=4, max_length=4, allow_null=True, required=False)
    data_collecting_type = serializers.SlugRelatedField(slug_field="code", queryset=DataCollectingType.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField(allow_null=True)
    pdu_fields = PDUFieldsUpdateSerializer(many=True)
    version = serializers.IntegerField(required=False)
    slug = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    partner_access = serializers.CharField(read_only=True)

    class Meta:
        model = Program
        fields = (
            "programme_code",
            "name",
            "slug",
            "sector",
            "description",
            "budget",
            "administrative_areas_of_implementation",
            "population_goal",
            "cash_plus",
            "frequency_of_payments",
            "data_collecting_type",
            "beneficiary_group",
            "start_date",
            "end_date",
            "pdu_fields",
            "version",
            "status",
            "partner_access",
        )

    def validate_programme_code(self, value: Optional[str]) -> Optional[str]:
        if value:
            value = validate_programme_code(value)
            if (
                Program.objects.filter(business_area=self.instance.business_area, programme_code=value)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError("Programme code is already used.")
        return value

    def validate_data_collecting_type(self, value: DataCollectingType) -> DataCollectingType:
        data_collecting_type = value
        validate_data_collecting_type(data_collecting_type, self.instance.business_area.slug)

        # validate if DCT can be updated
        if self.instance.data_collecting_type.code != value:
            # can update for draft program without population
            if self.instance.status != Program.DRAFT:
                raise serializers.ValidationError("Data Collecting Type can be updated only for Draft Programs.")
            else:
                if Household.objects.filter(program=self.instance).exists():
                    raise serializers.ValidationError(
                        "Data Collecting Type can be updated only for Program without any households."
                    )
        return value

    def validate_beneficiary_group(self, value: BeneficiaryGroup) -> BeneficiaryGroup:
        # validate if BG can be updated
        if self.instance.beneficiary_group != value and self.instance.registration_imports.exists():
            raise serializers.ValidationError("Beneficiary Group cannot be updated if Program has population.")
        return value

    def validate_version(self, value: Optional[int]) -> Optional[int]:
        check_concurrency_version_in_mutation(value, self.instance)
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        end_date = data.get("end_date")
        start_date = data["start_date"]
        if end_date:
            validate_end_date_after_start_date(start_date, end_date)

            if self.instance.cycles.filter(end_date__gt=end_date).exists():
                raise serializers.ValidationError(
                    {"end_date": "End date must be the same as or after the latest cycle."}
                )

        if self.instance.cycles.filter(start_date__lt=start_date).exists():
            raise serializers.ValidationError(
                {"start_date": "Start date must be the same as or before the earliest cycle."}
            )

        # validate DCT and BG combination
        data_collecting_type = data["data_collecting_type"]
        beneficiary_group = data["beneficiary_group"]
        validate_data_collecting_type_and_beneficiary_group_combination(data_collecting_type, beneficiary_group)
        return data

    def to_representation(self, obj: Program) -> Dict:
        """
        Override to_representation to include the partners and pdu_fields in the correct format.
        """
        representation = super().to_representation(obj)
        partners_qs = (
            Partner.objects.filter(
                Q(role_assignments__program=obj)
                | (Q(role_assignments__program=None) & Q(role_assignments__business_area=obj.business_area))
            )
            .annotate(partner_program=Value(obj.id))
            .order_by("name")
            .distinct()
        )
        representation["partners"] = PartnerForProgramSerializer(partners_qs, many=True).data
        representation["pdu_fields"] = PeriodicFieldSerializer(
            FlexibleAttribute.objects.filter(type=FlexibleAttribute.PDU, program=obj).order_by("name"), many=True
        ).data
        return representation


class ProgramUpdatePartnerAccessSerializer(serializers.ModelSerializer):
    partners = PartnersDataSerializer(many=True)
    version = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = Program
        fields = (
            "partners",
            "partner_access",
            "version",
        )

    def validate_version(self, value: Optional[int]) -> Optional[int]:
        check_concurrency_version_in_mutation(value, self.instance)
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # validate partners and partner_access
        partners = data.get("partners", [])
        partner_access = data["partner_access"]
        partner = self.context["request"].user.partner
        validate_partners_data(partners, partner_access, partner)
        return data


class ProgramCopySerializer(serializers.ModelSerializer):
    programme_code = serializers.CharField(min_length=4, max_length=4, allow_null=True, required=False)
    data_collecting_type = serializers.SlugRelatedField(slug_field="code", queryset=DataCollectingType.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField(allow_null=True)
    partners = PartnersDataSerializer(many=True)
    pdu_fields = PDUFieldsCreateSerializer(many=True)

    class Meta:
        model = Program
        fields = (
            "programme_code",
            "name",
            "sector",
            "description",
            "budget",
            "administrative_areas_of_implementation",
            "population_goal",
            "cash_plus",
            "frequency_of_payments",
            "data_collecting_type",
            "beneficiary_group",
            "start_date",
            "end_date",
            "pdu_fields",
            "partners",
            "partner_access",
        )

    def validate_programme_code(self, value: Optional[str]) -> Optional[str]:
        if value:
            value = validate_programme_code(value)
            if Program.objects.filter(business_area=self.instance.business_area, programme_code=value).exists():
                raise serializers.ValidationError("Programme code is already used.")
        return value

    def validate_data_collecting_type(self, value: DataCollectingType) -> DataCollectingType:
        data_collecting_type = value
        validate_data_collecting_type(data_collecting_type, self.instance.business_area.slug)
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        original_program = self.instance

        # validate DCT against original program
        data_collecting_type = data["data_collecting_type"]
        beneficiary_group = data["beneficiary_group"]
        if not original_program.data_collecting_type:
            raise serializers.ValidationError(
                {"data_collecting_type": "The original Program must have a Data Collecting Type."}
            )
        elif data_collecting_type not in original_program.data_collecting_type.compatible_types.all():
            raise serializers.ValidationError(
                {"data_collecting_type": "Data Collecting Type must be compatible with the original Program."}
            )

        # validate start_date and end_date
        end_date = data.get("end_date")
        if end_date:
            validate_end_date_after_start_date(data["start_date"], end_date)

        # validate DCT and BG combination
        validate_data_collecting_type_and_beneficiary_group_combination(data_collecting_type, beneficiary_group)

        # validate partners and partner_access
        partners = data.get("partners", [])
        partner_access = data["partner_access"]
        partner = self.context["request"].user.partner
        validate_partners_data(partners, partner_access, partner)
        return data


class ProgramSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = (
            "id",
            "programme_code",
            "slug",
            "name",
            "status",
        )


class ProgramCycleSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramCycle
        fields = (
            "id",
            "title",
        )
