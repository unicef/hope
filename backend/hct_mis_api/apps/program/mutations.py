import graphene
from django.db import transaction

from core.models import Location
from core.permissions import is_authenticated
from core.utils import decode_id_string
from core.validators import CommonValidator
from program.models import Program, CashPlan
from program.schema import ProgramNode, CashPlanNode
from program.validators import ProgramValidator, CashPlanValidator
from targeting.models import TargetPopulation


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    start_date = graphene.DateTime()
    end_date = graphene.DateTime()
    description = graphene.String()
    program_ca_id = graphene.String()
    location_id = graphene.String()
    budget = graphene.Float()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()


class UpdateProgramInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    name = graphene.String()
    status = graphene.String()
    start_date = graphene.DateTime()
    end_date = graphene.DateTime()
    description = graphene.String()
    program_ca_id = graphene.String()
    location_id = graphene.String()
    budget = graphene.Float()
    frequency_of_payments = graphene.String()
    sector = graphene.String()
    scope = graphene.String()
    cash_plus = graphene.Boolean()
    population_goal = graphene.Int()


class CreateCashPlanInput(graphene.InputObjectType):
    program_id = graphene.String()
    name = graphene.String()
    start_date = graphene.DateTime()
    end_date = graphene.DateTime()
    disbursement_date = graphene.DateTime()
    number_of_households = graphene.Int()
    coverage_duration = graphene.Int()
    coverage_units = graphene.String()
    target_population_id = graphene.String()
    cash_assist_id = graphene.String()
    distribution_modality = graphene.String()
    fsp = graphene.String()
    status = graphene.String()
    currency = graphene.String()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    dispersion_date = graphene.Date()


class UpdateCashPlanInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    program_id = graphene.String()
    name = graphene.String()
    start_date = graphene.DateTime()
    end_date = graphene.DateTime()
    disbursement_date = graphene.DateTime()
    number_of_households = graphene.Int()
    coverage_duration = graphene.Int()
    coverage_units = graphene.String()
    target_population_id = graphene.String()
    cash_assist_id = graphene.String()
    distribution_modality = graphene.String()
    fsp = graphene.String()
    status = graphene.String()
    currency = graphene.String()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    dispersion_date = graphene.Date()


class CreateProgram(CommonValidator, graphene.Mutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, program_data):
        location_id = decode_id_string(program_data.pop('location_id', None))
        location = Location.objects.get(id=location_id)

        cls.validate(
            start_date=program_data.get('start_date'),
            end_date=program_data.get('end_date'),
        )

        program = Program.objects.create(
            **program_data,
            location=location,
            status='DRAFT',
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
        program_id = decode_id_string(program_data.pop('id', None))

        program = Program.objects.select_for_update().get(id=program_id)

        location_id = decode_id_string(program_data.pop('location_id', None))

        if location_id:
            location = Location.objects.get(id=location_id)
            program.location = location

        cls.validate(
            program_data=program_data,
            program=program,
            start_date=program_data.get('start_date'),
            end_date=program_data.get('end_date'),
        )

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)

        program.save()

        return UpdateProgram(program)


class DeleteProgram(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        program_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get('program_id'))
        Program.objects.get(id=decoded_id).delete()
        return cls(ok=True)


class CreateCashPlan(CommonValidator, graphene.Mutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_data = CreateCashPlanInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, cash_plan_data):
        user = info.context.user
        program_id = decode_id_string(cash_plan_data.pop('program_id', None))
        target_population_id = decode_id_string(
            cash_plan_data.pop('target_population_id', None)
        )

        cls.validate(
            cash_plan_data=cash_plan_data,
            start_date=cash_plan_data.get('start_date'),
            end_date=cash_plan_data.get('end_date'),
        )

        cash_plan = CashPlan.objects.create(
            **cash_plan_data,
            created_by=user,
            target_population=TargetPopulation.objects.get(
                id=target_population_id,
            ),
            program=Program.objects.get(id=program_id),
        )

        return CreateCashPlan(cash_plan)


class UpdateCashPlan(CommonValidator, CashPlanValidator, graphene.Mutation):
    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_data = UpdateCashPlanInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, cash_plan_data):
        cash_plan_id = decode_id_string(cash_plan_data.pop('id', None))

        cash_plan = CashPlan.objects.select_for_update().get(id=cash_plan_id)

        program_id = decode_id_string(cash_plan_data.pop('program_id', None))
        if program_id:
            cash_plan.program = Program.objects.get(id=program_id)

        target_population_id = decode_id_string(
            cash_plan_data.pop('target_population_id', None)
        )
        if target_population_id:
            cash_plan.target_population = TargetPopulation.objects.get(
                id=target_population_id,
            )

        cls.validate(
            cash_plan_data=cash_plan_data,
            start_date=cash_plan_data.get('start_date'),
            end_date=cash_plan_data.get('end_date'),
        )

        for attrib, value in cash_plan_data.items():
            if hasattr(cash_plan, attrib):
                setattr(cash_plan, attrib, value)

        cash_plan.save()

        return UpdateCashPlan(cash_plan)


class DeleteCashPlan(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        cash_plan_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, **kwargs):
        decoded_id = decode_id_string(kwargs.get('cash_plan_id'))
        CashPlan.objects.get(id=decoded_id).delete()
        return cls(ok=True)


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
    create_cash_plan = CreateCashPlan.Field()
    update_cash_plan = UpdateCashPlan.Field()
    delete_cash_plan = DeleteCashPlan.Field()
