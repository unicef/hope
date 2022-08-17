import logging

import ast

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.documents import GrievanceTicketDocument

logger = logging.getLogger(__name__)


TERM_FIELDS = ("category", "assigned_to", "issue_type", "priority", "urgency", "grievance_type")
TERMS_FIELDS = ("status", "admin")


def execute_es_query(query_dict):
    es_response = (
        GrievanceTicketDocument
        .search()
        .params(search_type="dfs_query_then_fetch", preserve_order=True)
        .from_dict(query_dict)
    )

    es_ids = [hit.meta.id for hit in es_response.scan()]
    return es_ids


def create_es_query(options):
    all_queries = []
    query_search = []
    query_term_fields = []
    query_terms_fields = []

    grievance_status = options.pop("grievance_status", "active")
    created_at_range = options.pop("created_at_range", None)

    if created_at_range and created_at_range != "\"\"":
        created_at_range = ast.literal_eval(options.pop("created_at_range"))
        date_range = {
            "range": {
                "created_at": {}
            }
        }

        min_date = created_at_range.pop("min", None)
        if min_date:
            date_range["range"]["created_at"]["gte"] = min_date

        max_date = created_at_range.pop("max", None)
        if max_date:
            date_range["range"]["created_at"]["lte"] = max_date

        all_queries.append(date_range)

    search = options.pop("search", None)
    if search and search.strip():
        key, value = tuple(search.split(" ", 1))
        if key == "ticket_id":
            query_search.append({
                "term": {
                  "unicef_id": value
                }
            })
        elif key == "ticket_hh_id":
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
            if k == "assigned_to":
                v = decode_id_string(v)
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
                "status":  ["New", "Assigned", "In Progress", "On Hold", "For Approval"]
            }
        })

    all_queries.extend(query_term_fields)
    all_queries.extend(query_terms_fields)
    all_queries.extend(query_search)

    query_dict = {
        "query": {
            "bool": {
                "must": all_queries,
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

    return query_dict
