from typing import Dict, List, Optional, Union

from dateutil.parser import parse

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import NON_BENEFICIARY, RELATIONSHIP_UNKNOWN

KOBO_FORM_INDIVIDUALS_COLUMN_NAME = "individual_questions"


def reduce_asset(asset: Dict, *args, **kwargs) -> Dict:
    """
    Takes from asset only values that are needed by our frontend.

    {
        "uid": "aY2dvQ64KudGV5UdSvJkB6",
        "name": "Test",
        "sector": "Humanitarian - Education",
        "country": "Afghanistan",
        "asset_type": "survey",
        "date_modified": "2020-05-20T10:43:58.781178Z",
        "deployment_active": False,
        "has_deployment": False,
        "xls_link": "https://kobo.humanitarianresponse.info/
                     api/v2/assets/aY2dvQ64KudGV5UdSvJkB6.xls",
    }
    """
    download_link = ""
    for element in asset["downloads"]:
        if element["format"] == "xls":
            download_link = element["url"]

    settings = asset.get("settings")
    country = None
    sector = None

    if settings:
        if settings.get("sector"):
            sector = settings["sector"].get("label")
        if settings.get("country"):
            country = settings["country"].get("label")

    return {
        "id": asset["uid"],
        "name": asset["name"],
        "sector": sector,
        "country": country,
        "asset_type": asset["asset_type"],
        "date_modified": parse(asset["date_modified"]),
        "deployment_active": asset["deployment__active"],
        "has_deployment": asset["has_deployment"],
        "xls_link": download_link,
    }


def get_field_name(field_name: str) -> str:
    if "/" in field_name:
        return field_name.split("/")[-1]
    else:
        return field_name


def reduce_assets_list(assets: list, deployed: bool = True, *args, **kwarg) -> List:
    if deployed:
        return [reduce_asset(asset) for asset in assets if asset["has_deployment"] and asset["deployment__active"]]
    return [reduce_asset(asset) for asset in assets]


def count_population(results: list, business_area: BusinessArea) -> tuple[int, int]:
    from hashlib import sha256

    from hct_mis_api.apps.core.utils import rename_dict_keys
    from hct_mis_api.apps.registration_datahub.models import KoboImportedSubmission
    from hct_mis_api.apps.registration_datahub.tasks.utils import (
        get_submission_metadata,
    )

    total_households_count = 0
    total_individuals_count = 0
    seen_hash_keys = []
    for result in results:
        submission_meta_data = get_submission_metadata(result)

        if business_area.get_sys_option("ignore_amended_kobo_submissions"):
            submission_meta_data["amended"] = False

        submission_exists = KoboImportedSubmission.objects.filter(**submission_meta_data).exists()
        if submission_exists is False:
            total_households_count += 1
            for individual_data in result[KOBO_FORM_INDIVIDUALS_COLUMN_NAME]:
                fields = {
                    "given_name_i_c": None,
                    "middle_name_i_c": None,
                    "family_name_i_c": None,
                    "full_name_i_c": None,
                    "gender_i_c": None,
                    "birth_date_i_c": None,
                    "estimated_birth_date_i_c": None,
                    "phone_no_i_c": None,
                    "phone_no_alternative_i_c": None,
                }
                reduced_submission = rename_dict_keys(individual_data, get_field_name)
                for field_name in fields:
                    fields[field_name] = str(reduced_submission.get(field_name))
                hash_key = sha256(";".join(fields.values()).encode()).hexdigest()
                seen_hash_keys.append(hash_key)
                total_individuals_count += 1
                if (
                    reduced_submission.get("relationship_i_c", RELATIONSHIP_UNKNOWN).upper() == NON_BENEFICIARY
                    and seen_hash_keys.count(hash_key) > 1
                ):
                    total_individuals_count -= 1

    return total_households_count, total_individuals_count


def filter_by_owner(data: Union[List, Dict], business_area) -> Optional[Union[List, Dict]]:
    kobo_username = business_area.kobo_username
    if isinstance(data, list):
        return [element for element in data if element["owner__username"] == kobo_username]
    if data["owner__username"] == kobo_username:
        return data
    return None
