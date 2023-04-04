import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union

from django.db.models import QuerySet

import graphene
from graphene import Connection
from graphene.relay import PageInfo
from graphene_django import DjangoConnectionField
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    connection_from_list_slice,
    cursor_to_offset,
    get_offset_with_default,
    offset_to_cursor,
)

from hct_mis_api.apps.core.utils import save_data_in_cache

logger = logging.getLogger(__name__)


class DjangoFastConnectionField(DjangoConnectionField):
    use_cached_count = True

    @classmethod
    def cache_count(cls, connection: Connection, args: Dict, iterable: QuerySet) -> int:
        try:
            excluded_args = ["first", "last", "before", "after"]
            business_area = args.get("business_area")
            important_args = {k: str(v) for k, v in args.items() if k not in excluded_args}
            hashed_args = hashlib.sha1(json.dumps(important_args).encode()).hexdigest()
            cache_key = f"count_{business_area}_{connection}_{hashed_args}"
            return save_data_in_cache(cache_key, lambda: iterable.count(), 60 * 5)
        except Exception as e:
            logger.exception(e)
            return iterable.count()

    @classmethod
    def resolve_connection(
        cls, connection: Connection, args: Dict, iterable: Union[QuerySet, List], max_limit: Optional[int] = None
    ) -> Connection:
        # Remove the offset parameter and convert it to an after cursor.
        offset = args.pop("offset", None)
        after = args.get("after")
        if offset:
            if after:
                offset += cursor_to_offset(after) + 1
            # input offset starts at 1 while the graphene offset starts at 0
            args["after"] = offset_to_cursor(offset - 1)

        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            if cls.use_cached_count:
                list_length = DjangoFastConnectionField.cache_count(connection, args, iterable)
            else:
                list_length = iterable.count()
        else:
            list_length = len(iterable)
        list_slice_length = min(max_limit, list_length) if max_limit is not None else list_length

        # If after is higher than list_length, connection_from_list_slice
        # would try to do a negative slicing which makes django throw an
        # AssertionError
        after = min(get_offset_with_default(args.get("after"), -1) + 1, list_length)

        if max_limit is not None and "first" not in args:
            if "last" in args:
                args["first"] = list_length
                list_slice_length = list_length
            else:
                args["first"] = max_limit

        connection = connection_from_list_slice(
            iterable[after:],
            args,
            slice_start=after,
            list_length=list_length,
            list_slice_length=list_slice_length,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection


class ExtendedConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info: Any, **kwargs: Any) -> int:
        return root.length

    def resolve_edge_count(root, info: Any, **kwargs: Any) -> int:
        return len(root.edges)
