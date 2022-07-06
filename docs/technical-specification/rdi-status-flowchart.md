# Registration data import status flow chart

Open it in https://mermaid.ink/

```
graph TD
    DIA[DIIA - Automatic task] -->|celery task| IMPORTING
    FLEX[Flex Registration - Automatic task] -->|celery task| IMPORTING
    EXCEL[Excel - upload file] -->|celery task| IMPORTING
    KOBO[Kobo - Select Project] -->|celery task| IMPORTING

    IMPORTING(STATUS - IMPORTING)
    IMPORT_ERROR(STATUS - IMPORT ERROR)
    DEDUPLICATION(STATUS - DEDUPLICATION)
    DEDUPLICATION_FAILED(STATUS - DEDUPLICATION FAILED)
    IN_REVIEW(STATUS - IN REVIEW)
    REFUSED(STATUS - REFUSED)
    MERGING(STATUS - MERGING)
    MERGE_ERROR(STATUS - MERGE ERROR)
    MERGED(STATUS - MERGED)

    IMPORTING --> |celery task| DEDUPLICATION
    IMPORTING --> |error| IMPORT_ERROR
    DEDUPLICATION --> |celery task| DEDUPLICATION_FAILED
    DEDUPLICATION --> IN_REVIEW
    DEDUPLICATION_FAILED-->|rerun deduplication| DEDUPLICATION_FAILED
    DEDUPLICATION_FAILED-->|rerun deduplication| IN_REVIEW
    IN_REVIEW -->|merge| MERGING
    IN_REVIEW -->|refuse| REFUSED
    MERGING --> MERGE_ERROR
    MERGING --> MERGED
```