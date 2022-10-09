import sys


def post_process_dedupe_results(record):
    # {"duplicates": [{"dob": "1965-11-05",
    #                   "score": 11.0,
    #                   "hit_id": "266704c0-d13c-4475-9445-52ad1f6d9cb8",
    #                   "location": null,
    #                   "full_name": "Lavone Burnham",
    #                   "proximity_to_score": 5.0
    #                 }],
    #  "possible_duplicates": []
    #  }
    max_score = 0
    min_score = sys.maxsize
    for field in [record.deduplication_batch_results, record.deduplication_golden_record_results]:
        if "duplicates" in field:
            duplicates = field["duplicates"]
            for entry in field["duplicates"]:
                max_score = max(max_score, entry["score"])
                min_score = min(min_score, entry["score"])
            field["score"] = {"max": max_score, "min": min_score, "qty": len(duplicates)}


def combine_collections(a, b, path=None, update=True):
    """merges b into a
    version from flex registration"""
    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                combine_collections(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            elif isinstance(a[key], list) and isinstance(b[key], list):
                for idx in range(len(b[key])):
                    a[key][idx] = combine_collections(
                        a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update
                    )
            elif update:
                a[key] = b[key]
            else:
                raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a
