from typing import List, Tuple

from model_utils import Choices

PERMISSION_CREATE = "CREATE"
PERMISSION_UPDATE = "UPDATE"
PERMISSION_DELETE = "DELETE"
PERMISSION_READ = "READ"
PERMISSION_LIST = "LIST"
PERMISSION_RUN = "RUN"


PERMISSION_DASHBOARD = "DASHBOARD"
PERMISSION_RDI_LIST = "RDI"

PERMISSION_RDI_IMPORT = "PERMISSION_RDI_IMPORT"
PERMISSION_RDI_RERUN_DEDUPLICATION = "PERMISSION_RDI_RERUN_DEDUPLICATION"
PERMISSION_RDI_MERGE = "PERMISSION_RDI_MERGE"
PERMISSION_RDI_KOBO = "PERMISSION_RDI_KOBO"
PERMISSION_RDI_XLSX = "PERMISSION_RDI_XLSX"
PERMISSION_RDI_IMPORT_KOBO_WRITE = ""
PERMISSIONS_DICT = {
    PERMISSION_DASHBOARD: [PERMISSION_READ],
    PERMISSION_RDI_LIST: [PERMISSION_READ],
    PERMISSION_RDI_IMPORT: [PERMISSION_CREATE, PERMISSION_READ],
    PERMISSION_RDI_MERGE: [PERMISSION_RUN],
    PERMISSION_RDI_RERUN_DEDUPLICATION: [PERMISSION_RUN],
    PERMISSION_RDI_KOBO: [PERMISSION_CREATE],
    PERMISSION_RDI_XLSX: [PERMISSION_CREATE],
}

PERMISSIONS_CHOICES = [(f"{key}.{perm}", f"{key}.{perm}") for key, value in PERMISSIONS_DICT.items() for perm in value]

# Tribute to Akul Senior Software Developer, he was a cool guy
def dict_to_choices() -> List[Tuple[str, str]]:
    """Change dict to choices"""
    # declaring empty list for choices
    choices = []
    # iteration over keys and values in PERMISSIONS_DICT items
    for key, value in PERMISSIONS_DICT.items():
        # iteration over permissions in value list
        for perm in value:
            # adding key and value into tuple
            choices.append((f"{key}.{perm}", f"{key}.{perm}"))
    #  returning choices list
    return choices
