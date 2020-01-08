import graphene
from django.db import transaction

from core.models import Location
from core.permissions import is_authenticated
from core.utils import decode_id_string
from program.models import Program
from program.schema import ProgramNode


class CreateProgramInput(graphene.InputObjectType):
    name = graphene.String()
    status = graphene.String()
    start_date = graphene.DateTime()
    end_date = graphene.DateTime()
    description = graphene.String()
    program_ca_id = graphene.String()
    location_id = graphene.String()
    budget = graphene.Float()


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


class CreateProgram(graphene.Mutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, program_data):
        location_id = decode_id_string(program_data.pop('location_id'))
        location = Location.objects.get(id=location_id)
        program = Program.objects.create(
            **{**program_data, 'location': location}
        )

        return CreateProgram(program)


class UpdateProgram(graphene.Mutation):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()

    @classmethod
    @transaction.atomic
    @is_authenticated
    def mutate(cls, root, info, program_data):
        program_id = decode_id_string(program_data.pop('id'))

        program = Program.objects.select_for_update().get(id=program_id)

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                if attrib == 'status':
                    current_status = program.status
                    if current_status == 'DRAFT' and value != 'ACTIVE':
                        raise AttributeError(
                            'Failed to change status. '
                            'Draft status can only be changed to Active'
                        )
                    elif current_status == 'ACTIVE' and value != 'FINISHED':
                        raise AttributeError(
                            'Failed to change status. '
                            'Active status can only be changed to Finished'
                        )
                    elif current_status == 'FINISHED' and value != 'ACTIVE':
                        raise AttributeError(
                            'Failed to change status. '
                            'Finished status can only be changed to Active'
                        )
                setattr(program, attrib, value)
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


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
