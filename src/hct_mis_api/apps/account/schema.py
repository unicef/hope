from typing import Any

from django.contrib.auth import get_user_model

import graphene


class Query(graphene.ObjectType):
    has_available_users_to_export = graphene.Boolean(business_area_slug=graphene.String(required=True))

    def resolve_has_available_users_to_export(self, info: Any, business_area_slug: str) -> bool:
        return (
            get_user_model()
            .objects.prefetch_related("role_assignments")
            .filter(is_superuser=False, role_assignments__business_area__slug=business_area_slug)
            .exists()
        )
