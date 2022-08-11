import logging

import ast

from .documents import GrievanceTicketDocument

logger = logging.getLogger(__name__)


TERM_FIELDS = ("category", "assigned_to", "issue_type", "priority", "urgency", "grievance_type")
TERMS_FIELDS = ("status", "admin")


def execute_query(query_dict):
    es_response = (
        GrievanceTicketDocument
        .search()
        .params(search_type="dfs_query_then_fetch")
        .from_dict(query_dict)
        .execute()
    )

    es_ids = [x.meta["id"] for x in es_response]
    return es_ids


def search_es(options):
    all_queries = []
    query_search = []
    query_term_fields = []
    query_terms_fields = []

    size = options.pop("first", 10)
    grievance_status = options.pop("grievance_status")
    created_at_range = ast.literal_eval(options.pop("created_at_range"))

    if created_at_range != "":
        date_range = {
            "range": {
                "created_at": {}
            }
        }

        min_date = created_at_range.pop("min")
        if min_date:
            date_range["range"]["created_at"]["gte"] = min_date

        max_date = created_at_range.pop("max")
        if max_date:
            date_range["range"]["created_at"]["lte"] = max_date

        all_queries.append(date_range)

    search = options.pop("search")
    if search.strip():
        key, value = tuple(search.split(" ", 1))
        if key == "ticket_id":
            return execute_query({
              "query": {
                "term": {
                  "_id": value
                }
              }
            })
        elif key == "ticket_hhid":
            query_search.append({
                "term": {
                    "household_unicef_id": {
                        "value": value
                    }
                }
            })
        else:
            query_search.append({
                "term": {
                    "head_of_household_last_name": {
                        "value": value
                    }
                }
            })

    order_by = options.pop("order_by", "-created_at")
    if order_by[0] == "-":
        sort = {
            order_by[1:]: {
                "order": "desc",
                "unmapped_type": "date"
            }
        }
    else:
        sort = {
            order_by: {
                "order": "asc",
                "unmapped_type": "date"
            }
        }

    for k, v in options.items():
        if k in TERM_FIELDS and v:
            query_term_fields.append({
                "term": {
                    k: {
                        "value": v
                    }
                }
            })

        if k in TERMS_FIELDS and v not in ([""], [None]):
            query_terms_fields.append({
                "terms": {
                    k: v
                }
            })

    if grievance_status == "active":
        query_terms_fields.append({
            "terms": {
                "grievance_status":  ["New", "Assigned", "In Progress", "On Hold", "For Approval"]
            }
        })

    all_queries.extend(query_term_fields)
    all_queries.extend(query_terms_fields)
    all_queries.extend(query_search)

    query_dict = {
        "size": size,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
        "sort": [sort]
    }

    business_area = options.pop("business_area")
    if business_area:
        query_dict["query"]["bool"]["filter"] = {
            "term": {
                "business_area": "afghanistan"
            }
        }

    first = options.pop("first", 10)
    after = options.pop("after", 1)

    return execute_query(query_dict)
