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


def merge(final_collection, additional_collection):
    """merges additional collection into final collection"""
    for key in additional_collection:
        if key in final_collection:
            if isinstance(final_collection[key], dict) and isinstance(additional_collection[key], dict):
                merge(final_collection[key], additional_collection[key])
            elif final_collection[key] == additional_collection[key]:
                pass  # same leaf value
            elif isinstance(final_collection[key], list) and isinstance(additional_collection[key], list):
                for idx, val in enumerate(additional_collection[key]):
                    final_collection[key][idx] = merge(final_collection[key][idx], additional_collection[key][idx])
            else:
                final_collection[key] = additional_collection[key]
        else:
            final_collection[key] = additional_collection[key]
    return final_collection
