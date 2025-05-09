from datetime import date
from typing import Any

import graphene
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64


class DeduplicationResultNode(graphene.ObjectType):
    unicef_id = graphene.String()
    hit_id = graphene.ID()
    full_name = graphene.String()
    score = graphene.Float()
    proximity_to_score = graphene.Float()
    location = graphene.String()
    age = graphene.Int()
    duplicate = graphene.Boolean()
    distinct = graphene.Boolean()

    def resolve_age(self, info: Any) -> int | None:
        date_of_birth = self.get("dob")
        if date_of_birth:
            today = date.today()
            return relativedelta(today, parse(date_of_birth)).years
        return None

    def resolve_location(self, info: Any) -> str:
        return self.get("location", "Not provided")

    def resolve_duplicate(self, info: Any) -> bool:
        return self.get("duplicate", False)

    def resolve_distinct(self, info: Any) -> bool:
        return self.get("distinct", False)

    def resolve_unicef_id(self, info: Any) -> str:
        from hct_mis_api.apps.household.models import Individual

        individual = Individual.all_objects.get(id=decode_id_string(self.get("hit_id")))
        return str(individual.unicef_id)


class DeduplicationEngineSimilarityPairIndividualNode(graphene.ObjectType):
    id = graphene.String()
    photo = graphene.String()
    full_name = graphene.String()
    unicef_id = graphene.String()
    # optional for RDI population view duplicates modal:
    similarity_score = graphene.Float()
    age = graphene.Int()
    location = graphene.String()

    @staticmethod
    def resolve_photo(parent: Any, info: Any) -> graphene.String | None:
        from hct_mis_api.apps.household.models import Individual

        # photo url serialization storage timeout
        individual = Individual.all_objects.get(id=parent.get("id"))
        return individual.photo.url if individual.photo else None

    @staticmethod
    def resolve_id(parent: Any, info: Any) -> str | None:
        return encode_id_base64(parent.get("id"), "Individual")


class DeduplicationEngineSimilarityPairNode(BaseNodePermissionMixin, graphene.ObjectType):
    permission_classes = (hopePermissionClass(Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS),)

    individual1 = graphene.Field(DeduplicationEngineSimilarityPairIndividualNode)
    individual2 = graphene.Field(DeduplicationEngineSimilarityPairIndividualNode)
    similarity_score = graphene.String()
