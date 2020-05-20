from dateutil.parser import parse


def reduce_asset(asset: dict) -> dict:
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
        "xls_link": "https://kobo.humanitarianresponse.info/api/v2/assets/aY2dvQ64KudGV5UdSvJkB6.xls",
    }
    """
    download_link = ""
    for element in asset["downloads"]:
        if element["format"] == "xls":
            download_link = element["url"]

    return {
        "uid": asset["uid"],
        "name": asset["name"],
        "sector": asset["settings"]["sector"]["label"],
        "country": asset["settings"]["country"]["label"],
        "asset_type": asset["asset_type"],
        "date_modified": parse(asset["date_modified"]),
        "deployment_active": asset["deployment__active"],
        "has_deployment": asset["has_deployment"],
        "xls_link": download_link,
    }


def reduce_assets_list(assets: list, only_deployed: bool = False) -> list:
    if only_deployed:
        return [
            reduce_asset(asset)
            for asset in assets
            if asset["has_deployment"] and asset["deployment_active"]
        ]
    return [reduce_asset(asset) for asset in assets]
