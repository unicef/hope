"""Helpers for asserting on the *shape* of the SQL a list endpoint builds.

Written for the grievance list optimisations (ticket 331051), which replace joins onto
big m2m tables with correlated `EXISTS` subqueries.

    with CaptureQueriesContext(connection) as captured:
        response = api_client(user).get(list_url(afghanistan))

    assert "grievance_grievanceticket_programs" not in joined_tables(list_queryset(response))
    assert '"grievance_grievanceticket"."id" IN (SELECT' not in main_list_statement(
        captured, "grievance_grievanceticket"
    )

Why assert on SQL at all:

- The rewrites change neither the response body nor the number of queries, only how many
  rows the database scans. SQL is the only place a regression shows.
- The ticket -> program join does have one behavioural symptom, duplicate rows, covered by
  `test_list_returns_ticket_once_when_linked_to_multiple_programs` and others. But
  `.distinct()` hides it, so a rewrite that brings the join back *and* adds a `.distinct()`
  is correct at the old cost with every behavioural test still green. That is what these
  assertions catch.
"""

from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext
from rest_framework.response import Response


def list_queryset(response: Response) -> QuerySet:
    """The queryset the view used for this request, with filter backends applied.

    Returned unevaluated, ready to inspect with `joined_tables`.
    """
    view = response.renderer_context["view"]
    return view.filter_queryset(view.get_queryset())


def joined_tables(queryset: QuerySet) -> set[str]:
    """Table names in the query's FROM clause: the base table plus every table it joins.

    Tables used only inside a correlated subquery (`Exists`, `Subquery`) are not in the
    FROM clause, so they are not returned - which is what makes this useful for telling a
    join apart from an `EXISTS`.
    """
    query = queryset.query
    return {join.table_name for alias, join in query.alias_map.items() if query.alias_refcount[alias]}


def main_list_statement(
    captured: CaptureQueriesContext,
    table: str,
    *,
    order_by: str = "created_at",
    descending: bool = True,
) -> str:
    """SQL text of the statement that fetched one page of rows from `table`.

    - It is picked out of `captured` by the endpoint's ORDER BY plus a LIMIT, which is what
      tells it apart from the count query (no ORDER BY) and from the prefetches that follow.
    - `order_by` must name the field the endpoint under test really sorts by; the default
      matches the grievance list.
    - `table` is required so a caller cannot silently match some other model's statement.
    - If the same statement ran twice, the first one is returned.
    """
    direction = "DESC" if descending else "ASC"
    ordering = f'ORDER BY "{table}"."{order_by}" {direction}'
    for query in captured.captured_queries:
        if ordering in query["sql"] and "LIMIT" in query["sql"]:
            return query["sql"]
    raise AssertionError(
        f"No paginated statement matching '{ordering}' among {len(captured.captured_queries)} "
        f"captured queries. Check that the request was made inside the capture block and that "
        f"the endpoint orders by '{order_by}' {direction}."
    )
