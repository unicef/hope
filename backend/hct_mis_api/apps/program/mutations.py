import graphene
from django.db import transaction

from core.models import Location, BusinessArea
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import CommonValidator
from program.models import Program, CashPlan
from program.schema import ProgramNode, CashPlanNode
from program.validators import (
    ProgramValidator,
    CashPlanValidator,
    ProgramDeletionValidator,
)
from targeting.models import TargetPopulation


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    program_ca_id = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()


class UpdateProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    status = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    program_ca_id = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()


class CreateProgram(CommonValidator, graphene.Mutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, program_data):
        business_area_slug = program_data.pop("business_area_slug", None)
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.validate(
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
        )

        program = Program.objects.create(
            **program_data, status="DRAFT", business_area=business_area,
        )

        return CreateProgram(program)


class UpdateProgram(CommonValidator, ProgramValidator, graphene.Mutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, program_data):
        program_id = decode_id_string(program_data.pop("id", None))

        program = Program.objects.select_for_update().get(id=program_id)

        business_area_slug = program_data.pop("business_area_slug", None)

        if business_area_slug:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            program.business_area = business_area

        cls.validate(
            program_data=program_data,
            program=program,
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
        )

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)

        program.save()

        return UpdateProgram(program)


class DeleteProgram(ProgramDeletionValidator, graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        program_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get("program_id"))
        program = Program.objects.get(id=decoded_id)

        cls.validate(program=program)

        program.delete()

        return cls(ok=True)


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
