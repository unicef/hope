from typing import Any, Dict, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import Program, ProgramCycle


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

    class Meta:
        model = ProgramCycle
        fields = (
            "id",
            "unicef_id",
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
        )

    def get_created_by(self, obj: ProgramCycle) -> str:
        if not obj.created_by:
            return "-"
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"


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
        program = self.get_program(self.context["request"].parser_context["kwargs"]["program_id"])
        data["program"] = program
        data["created_by"] = self.context["request"].user
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if program.status != Program.ACTIVE:
            raise serializers.ValidationError("Create Programme Cycle is possible only for Active Programme.")

        if start_date and start_date < program.start_date:
            raise serializers.ValidationError(
                {"start_date": "Programme Cycle start date cannot be earlier than programme start date"}
            )
        if end_date and end_date > program.end_date:
            raise serializers.ValidationError(
                {"end_date": "Programme Cycle end date cannot be later than programme end date"}
            )

        if program.cycles.filter(end_date__isnull=True).exists():
            raise serializers.ValidationError("All Programme Cycles should have end date for creation new one.")

        # timeframes overlapping
        validate_cycle_timeframes_overlapping(program, start_date, end_date)
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
            ProgramCycle.objects.filter(title=value, program=self.instance.program, is_removed=False)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise serializers.ValidationError("A ProgramCycle with this title already exists.")

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        program = self.instance.program
        if program.status != Program.ACTIVE:
            raise serializers.ValidationError("Update Programme Cycle is possible only for Active Programme.")

        if self.instance.end_date and "end_date" in data and data.get("end_date") is None:
            raise serializers.ValidationError(
                {
                    "end_date": "Not possible leave the Programme Cycle end date empty if it was not empty upon starting the edit."
                }
            )
        validate_cycle_timeframes_overlapping(program, data.get("start_date"), data.get("end_date"), self.instance.pk)
        return data


class ProgramCycleDeleteSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = ProgramCycle
        fields = ["id"]
