from typing import Any, Dict, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.core.utils import decode_id_string
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


class ProgramCycleListSerializer(EncodedIdSerializerMixin):
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


class ProgramCycleCreateSerializer(EncodedIdSerializerMixin):
    title = serializers.CharField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=False)

    class Meta:
        model = ProgramCycle
        fields = ["title", "start_date", "end_date"]

    @staticmethod
    def get_program(program_id: str) -> Program:
        program = get_object_or_404(Program, id=decode_id_string(program_id))
        return program

    def validate_title(self, value: str) -> str:
        program = self.get_program(self.context["request"].parser_context["kwargs"]["program_id"])
        cycles = program.cycles.all()
        if cycles.filter(title=value).exists():
            raise serializers.ValidationError({"title": "Programme Cycles' title should be unique."})
        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        request = self.context["request"]
        program = self.get_program(request.parser_context["kwargs"]["program_id"])
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


class ProgramCycleUpdateSerializer(EncodedIdSerializerMixin):
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
            raise serializers.ValidationError("A ProgramCycle with this title already exists.")

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


class ProgramCycleDeleteSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = ProgramCycle
        fields = ["id"]


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
