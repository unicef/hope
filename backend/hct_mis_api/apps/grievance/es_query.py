import ast


def create_grievance_es_query(kwargs):
    all_queries = []
    query_search = []
    query_term_fields = []
    query_terms_fields = []

    size = kwargs.pop("first", 10)
    grievance_status = kwargs.pop("grievance_status")
    created_at_range = kwargs.pop("created_at_range")

    term_fields = ("category", "assigned_to", "issue_type", "priority", "urgency", "grievance_type")
    terms_fields = ("status", "admin")

    if created_at_range:
        created_at_range = ast.literal_eval(created_at_range)
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

    search = kwargs.pop("search")
    if search:
        key, value = tuple(search.split(" ", 1))
        if key == "ticket_id":
            query_search.append({
                "term": {
                    "_id": {
                        "value": value
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

    order_by = kwargs.pop("order_by", "-created_at")
    if order_by[0] == "-":
        sort = {
            order_by[1:]: {
                "order": "desc"
            }
        }
    else:
        sort = {
            order_by: {
                "order": "asc"
            }
        }

    for k, v in kwargs.items():
        if k in term_fields and v:
            query_term_fields.append({
                "term": {
                    k: {
                        "value": v
                    }
                }
            })

        if k in terms_fields and v != [""]:
            query_terms_fields.append({
                "terms": {
                    k: {
                        "value": v
                    }
                }
            })

    if grievance_status == "active":
        query_terms_fields.append({
            "terms": {
                "grievance_status": {
                    "value": ["New", "Assigned", "In Progress", "On Hold", "For Approval"]
                }
            }
        })

    all_queries.extend(query_term_fields)
    all_queries.extend(query_terms_fields)
    all_queries.extend(query_search)

    query = {
        "size": size,
        "query": {
            "bool": {
                "minimum_should_match": 1,
                "should": all_queries,
            }
        },
        "sort": [sort]
    }

    business_area = kwargs.pop("business_area")
    if business_area:
        query["query"]["bool"]["filter"] = {
            "term": {
                "business_area": "afghanistan"
            }
        }

    return query
