from dateutil.parser import parse


KOBO_FORM_INDIVIDUALS_COLUMN_NAME = "individual_questions"


def reduce_asset(asset: dict, *args, **kwargs) -> dict:
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


def reduce_assets_list(
    assets: list, only_deployed: bool = False, *args, **kwarg
) -> list:
    if only_deployed:
        return [
            reduce_asset(asset)
            for asset in assets
            if asset["has_deployment"] and asset["deployment_active"]
        ]
    return [reduce_asset(asset) for asset in assets]


def count_population(results: list):
    total_individuals_count = 0
    for result in results:
        total_individuals_count += len(
            result[KOBO_FORM_INDIVIDUALS_COLUMN_NAME]
        )

    total_households_count = len(results)

    return total_households_count, total_individuals_count
