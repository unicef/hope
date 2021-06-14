import logging

from django.conf import settings
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.core.exceptions import ValidationError

import requests

from hct_mis_api.apps.core.models import AdminArea, AdminAreaLevel

logger = logging.getLogger(__name__)


class DatamartAPI:
    PAGE_SIZE = 100
    LOCATIONS_ENDPOINT = "/api/latest/datamart/locations/?-serializer=geo&format=json&ordering=id"

    def __init__(self):
        self._client = requests.session()
        self._init_auth()
        self.url = settings.DATAMART_URL
        self._location_cache = {}

    def _init_auth(self):
        self._client.auth = (settings.DATAMART_USER, settings.DATAMART_PASSWORD)

    def get_admin_levels(self, max_pages=None):
        url = f"/api/latest/datamart/gateway-type/?&page_size={DatamartAPI.PAGE_SIZE}"
        next_url = f"{self.url}{url}"
        results: list = []
        page = 1
        while next_url:
            data = self._handle_get_request(next_url, is_absolute_url=True)
            next_url = data["next"]
            for entry in data["results"]:
                yield entry
            if max_pages and page >= max_pages:
                break
            page += 1
        return results

    def get_location(self, id):
        url = f"/api/latest/datamart/locations/{id}/"
        return self._handle_get_request(url)

    def get_locations(self, *, country=None, gis=False, max_records=None, page_size=None):
        url = f"/api/latest/datamart/locations/?&page_size={page_size or self.PAGE_SIZE}"
        if country:
            url = f"{url}&country_name={country}"
        if gis:
            url = f"{url}&-serializer=gis"
        next_url = f"{self.url}{url}"
        records = 0
        while next_url:
            data = self._handle_get_request(next_url, is_absolute_url=True)
            next_url = data["next"]
            for entry in data["results"]:
                records += 1
                yield entry
                if max_records and records >= max_records:
                    break
            if max_records and records >= max_records:
                break

    def get_locations_geo_data(self, business_area):
        return self._get_paginated_results(
            f"{DatamartAPI.LOCATIONS_ENDPOINT}"
            f"&country_code={business_area.code}&page_size={DatamartAPI.PAGE_SIZE}"
            # f"{DatamartAPI.LOCATIONS_ENDPOINT}" f"&country_name={business_area.name}&page_size={DatamartAPI.PAGE_SIZE}"
        )

    def _features_to_multi_polygon(self, geometry):
        if geometry is None:
            return None
        geometry_type = geometry.get("type")
        if geometry_type != "MultiPolygon":
            logger.error("Geometry type should be MultiPolygon")
            raise ValidationError("Geometry type should be MultiPolygon")
        return MultiPolygon([Polygon(polygon) for polygon in geometry.get("coordinates")[0]])

    def generate_admin_areas(self, locations, business_area):
        admin_areas_to_create = []
        admin_areas_external_id_dict = {}
        admin_area_level_dict = {}
        for location in locations:
            properties = location.get("properties")
            gateway = properties.get("gateway")
            external_id = location.get("id")
            admin_area_level = admin_area_level_dict.get(gateway)
            if admin_area_level is None:
                admin_area_level = AdminAreaLevel.objects.filter(
                    admin_level=gateway, business_area=business_area
                ).first()
            if admin_area_level is None:
                admin_area_level = AdminAreaLevel(
                    admin_level=gateway, business_area=business_area, name=f"{business_area.name}-{gateway}"
                )
            admin_area_level_dict[gateway] = admin_area_level

            admin_area = AdminArea.objects.filter(external_id=external_id).first()
            if admin_area is None:
                admin_area = AdminArea()
            admin_area.external_id = external_id
            admin_area.title = properties.get("name")
            admin_area.admin_area_level = admin_area_level
            admin_area.p_code = properties.get("p_code")
            admin_area.point = Point(properties.get("longitude"), properties.get("latitude"))
            admin_area.geom = self._features_to_multi_polygon(location.get("geometry"))
            admin_areas_to_create.append(admin_area)
            admin_areas_external_id_dict[external_id] = admin_area

        # parent assigment
        for location in locations:
            properties = location.get("properties")
            external_id = location.get("id")
            parent_external_id = properties.get("parent")
            if parent_external_id is None:
                continue
            admin_area = admin_areas_external_id_dict.get(external_id)
            admin_area.parent = admin_areas_external_id_dict.get(parent_external_id)

        for _, admin_area_level in admin_area_level_dict.items():
            admin_area_level.save()
        for admin_area in admin_areas_to_create:
            self.recursive_save(admin_area)
        AdminArea.objects.rebuild()
        return admin_areas_to_create

    def recursive_save(self, admin_area):
        if admin_area.parent is not None:
            self.recursive_save(admin_area.parent)
        admin_area.save()

    def _handle_get_request(self, url, is_absolute_url=False) -> dict:
        if not is_absolute_url:
            url = f"{self._get_url()}{url}"
        response = self._client.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        return response.json()

    def _get_paginated_results(self, url, max_pages=None) -> list:
        next_url = f"{self._get_url()}{url}"
        results: list = []
        page = 1
        while next_url:
            data = self._handle_get_request(next_url, is_absolute_url=True)
            next_url = data["next"]
            results.extend(data["results"]["features"])
            if max_pages and page >= max_pages:
                break
            page += 1
        return results

    def _handle_post_request(self, url, data) -> dict:
        response = self._client.post(url=f"{self._get_url()}{url}", data=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        return response.json()

    def _get_url(self):
        return f"{self.url}"
