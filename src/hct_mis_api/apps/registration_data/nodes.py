from datetime import date
from typing import Any, Optional

import graphene
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


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
