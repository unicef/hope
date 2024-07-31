from typing import Any, Dict

from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import Program, ProgramCycle


class ProgramCycleListSerializer(EncodedIdSerializerMixin):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ProgramCycle
        fields = (
            "id",
            "unicef_id",
            "title",
            "status",
            "start_date",
            "end_date",
            "created_at",
            "total_entitled_quantity_usd",
            "total_undelivered_quantity_usd",
            "total_delivered_quantity_usd",
        )


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
            raise ValidationError("All Programme Cycles should have end date for creation new one.")

        # timeframes_overlapping
        if start_date and end_date:
            overlapping_cycles = program.cycles.all().filter(start_date__lt=end_date, end_date__gt=start_date)
            if overlapping_cycles.exists():
                raise ValidationError("Program Cycles' timeframes must not overlap.")
        elif start_date:
            overlapping_cycles = program.cycles.all().filter(start_date__lte=start_date, end_date__gte=start_date)
            if overlapping_cycles.exists():
                raise ValidationError("Program Cycles' timeframes must not overlap with the provided start date.")
        elif end_date:
            overlapping_cycles = program.cycles.all().filter(start_date__lte=end_date, end_date__gte=end_date)
            if overlapping_cycles.exists():
                raise ValidationError("Program Cycles' timeframes must not overlap with the provided end date.")

        return data


class ProgramCycleUpdateSerializer(EncodedIdSerializerMixin):
    title = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    class Meta:
        model = ProgramCycle
        fields = ["title", "start_date", "end_date"]

    def validate_title(self, value: str) -> str:
        value = value.strip()
        if ProgramCycle.objects.filter(title=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("A ProgramCycle with this title already exists.")

        if value is None or "":
            raise ValidationError("Not possible leave the Programme Cycle title empty.")

        return value

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        program = self.instance.program
        if program.status != Program.ACTIVE:
            raise serializers.ValidationError("Update Programme Cycle is possible only for Active Programme.")

        if data.get("start_date") is None:
            raise ValidationError("Not possible leave the Programme Cycle start date empty.")

        if not self.instance.end_date and data.get("end_date") is None:
            raise ValidationError(
                "Not possible leave the Programme Cycle end date empty if it was empty upon starting the edit."
            )

        return data


class ProgramCycleDeleteSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = ProgramCycle
        fields = ["id"]
