from typing import Any

import graphene
from constance import config


class Query(graphene.ObjectType):
    cash_assist_url_prefix = graphene.String()

    def resolve_cash_assist_url_prefix(parent, info: Any) -> str:
        return config.CASH_ASSIST_URL_PREFIX
