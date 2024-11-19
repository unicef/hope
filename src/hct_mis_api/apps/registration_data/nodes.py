from datetime import date
from typing import Any, Optional

import graphene
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    Permissions,
    hopePermissionClass,
)


class DeduplicationResultNode(graphene.ObjectType):
    hit_id = graphene.ID()
    full_name = graphene.String()
    score = graphene.Float()
    proximity_to_score = graphene.Float()
    location = graphene.String()
    age = graphene.Int()
    duplicate = graphene.Boolean()
    distinct = graphene.Boolean()

    def resolve_age(self, info: Any) -> Optional[int]:
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


class DeduplicationEngineSimilarityPairIndividualNode(graphene.ObjectType):
    photo = graphene.String()
    full_name = graphene.String()
    unicef_id = graphene.String()

    @staticmethod
    def resolve_photo(parent: Any, info: Any) -> Optional[graphene.String]:
        from hct_mis_api.apps.household.models import Individual

        individual = Individual.objects.get(unicef_id=parent.get("unicef_id"))
        return individual.photo.url if individual.photo else None


class DeduplicationEngineSimilarityPairNode(BaseNodePermissionMixin, graphene.ObjectType):
    permission_classes = (hopePermissionClass(Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS),)

    individual1 = graphene.Field(DeduplicationEngineSimilarityPairIndividualNode)
    individual2 = graphene.Field(DeduplicationEngineSimilarityPairIndividualNode)
    similarity_score = graphene.String()
