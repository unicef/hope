from typing import Any, Dict

import graphene


class ExtendedConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info: Any, **kwargs: Any) -> int:
        return root.length

    def resolve_edge_count(root, info: Any, **kwargs: Any) -> int:
        return len(root.edges)
