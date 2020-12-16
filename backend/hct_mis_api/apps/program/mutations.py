import graphene
from django.db import transaction

from account.permissions import PermissionMutation, Permissions
from core.models import BusinessArea
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import CommonValidator
from program.models import Program
from program.schema import ProgramNode
from program.validators import (
    ProgramValidator,
    ProgramDeletionValidator,
)


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()
    individual_data_needed = graphene.Boolean()


class UpdateProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    status = graphene.String()
    start_date = graphene.Date()
    end_date = graphene.Date()
    description = graphene.String()
    budget = graphene.Decimal()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()
    administrative_areas_of_implementation = graphene.String()
    business_area_slug = graphene.String()
    individual_data_needed = graphene.Boolean()


class CreateProgram(CommonValidator, PermissionMutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, program_data):
        business_area_slug = program_data.pop("business_area_slug", None)
        business_area = BusinessArea.objects.get(slug=business_area_slug)
        cls.has_permission(info, Permissions.PROGRAMME_CREATE, business_area)

        cls.validate(
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
        )

        program = Program.objects.create(
            **program_data,
            status=Program.DRAFT,
            business_area=business_area,
        )

        return CreateProgram(program)


class UpdateProgram(ProgramValidator, PermissionMutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, program_data):
        program_id = decode_id_string(program_data.pop("id", None))

        program = Program.objects.select_for_update().get(id=program_id)
        business_area = program.business_area

        # status update permissions if status is passed
        status_to_set = program_data.get("status")
        if status_to_set and program.status != status_to_set:
            if status_to_set == Program.ACTIVE:
                cls.has_permission(info, Permissions.PROGRAMME_ACTIVATE, business_area)
            elif status_to_set == Program.FINISHED:
                cls.has_permission(info, Permissions.PROGRAMME_FINISH, business_area)

        # permission if updating any other fields
        if [k for k, v in program_data.items() if k != "status"]:
            cls.has_permission(info, Permissions.PROGRAMME_UPDATE, business_area)

        # TODO: check if you can really update business area when editing programme (I don't see it in the form)
        # If you can, should we check for permission in both areas?
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


class DeleteProgram(ProgramDeletionValidator, PermissionMutation):
    ok = graphene.Boolean()

    class Arguments:
        program_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get("program_id"))
        program = Program.objects.get(id=decoded_id)

        cls.has_permission(info, Permissions.PROGRAMME_REMOVE, program.business_area)

        cls.validate(program=program)

        program.delete()

        return cls(ok=True)


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
