from typing import Any

import graphene
from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.household.models import Individual, FOSTER_CHILD, Document
from hct_mis_api.apps.household.schema import IndividualNode, DocumentNode


class ConfirmFosterChildRelationMutation(graphene.Mutation):
    individual = graphene.Field(IndividualNode)

    class Arguments:
        individual_id = graphene.Argument(graphene.ID, required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, individual_id: str) -> "ConfirmFosterChildRelationMutation":
        decoded_individual_id = decode_id_string(individual_id)
        individual = Individual.objects.filter(id=decoded_individual_id).first()
        if not(individual or individual.relationship != FOSTER_CHILD):
            raise ValidationError("Individual does not exist or is not in foster child relationship")

        individual.mark_relationship_as_confirmed()
        return cls(individual=individual)


class ClearDocumentMutation(graphene.Mutation):
    document = graphene.Field(DocumentNode)

    class Arguments:
        document_id = graphene.Argument(graphene.ID, required=True)
        cleared = graphene.Argument(graphene.Boolean, required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, document_id: str, cleared: bool) -> "ClearDocumentMutation":
        decoded_document_id = decode_id_string(document_id)
        document = Document.objects.filter(id=decoded_document_id).first()
        document.cleared = cleared
        document.save(update_fields=["cleared"])
        return cls(document=document)


class Mutations(graphene.ObjectType):
    confirm_foster_child_relation = ConfirmFosterChildRelationMutation.Field()
    clear_document = ClearDocumentMutation.Field()
