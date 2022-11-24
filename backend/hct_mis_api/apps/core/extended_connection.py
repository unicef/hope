import hashlib
import json

import graphene
from django.db.models import QuerySet
from graphene.relay import PageInfo
from graphene_django import DjangoConnectionField
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.arrayconnection import (
    cursor_to_offset,
    offset_to_cursor,
    get_offset_with_default,
    connection_from_list_slice,
)

from hct_mis_api.apps.core.utils import save_data_in_cache


class DjangoFastConnectionField(DjangoConnectionField):
    @classmethod
    def cache_count(cls, connection, args, iterable):
        try:
            excluded_args = ["first", "last", "before", "after"]
            business_area = args.get("business_area")
            important_args = {k: v for k, v in args.items() if k not in excluded_args}
            hashed_args = hashlib.sha1(json.dumps(important_args).encode()).hexdigest()
            cache_key = f"{connection}_count_{business_area}_{hashed_args}"
            return save_data_in_cache(cache_key, lambda: iterable.count(), 60 * 5)
        except:
            return iterable.count()

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
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
            list_length = DjangoFastConnectionField.cache_count(connection, args, iterable)
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

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)
