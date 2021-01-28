import requests
from django.conf import settings
from django.core.serializers import serialize
from hct_mis_api.apps.core.models import AdminArea, AdminAreaLevel


class DatamartAPI:
    PAGE_SIZE = 100
    LOCATIONS_ENDPOINT = "/api/latest/datamart/locations/?-serializer=geo&format=json&ordering=id"

    def __init__(self):
        self._client = requests.session()
        self._init_auth()
        self.url =settings.DATAMART_URL

    def _init_auth(self):
        self._client.auth = (settings.DATAMART_USER, settings.DATAMART_PASSWORD)

    def get_locations_std_data(self, business_area):
        return self._get_paginated_results(f"{self._get_url()}{DatamartAPI.LOCATIONS_ENDPOINT}"
                                           f"&country_name={business_area.name}&page_size={DatamartAPI.PAGE_SIZE}")

    def generate_admin_areas(self,locations,business_area):
        # external_id = models.CharField(
        #     title=models.CharField(max_length=255)
        # admin_area_level = models.ForeignKey(
        #     latitude=models.DecimalField(
        #         longitude=models.DecimalField(
        #             p_code=models.CharField(max_length=32, blank=True, null=True, verbose_name='Postal Code')
        # parent = TreeForeignKey(
        #     geom=models.MultiPolygonField(null=True, blank=True)
        # point = models.PointField(null=True, blank=True)
        # objects = AdminAreaManager()
        admin_areas_to_create = []
        admin_areas_external_id_dict = {}
        admin_area_level_dict = {}
        for location in locations:
            properties = location.get('properties')
            gateway= properties.get('gateway')
            external_id =properties.get('id')
            admin_area_level = admin_area_level_dict.get(gateway)
            if admin_area_level is None:
                admin_area_level = AdminAreaLevel(
                    admin_level=gateway,
                    name=f"{business_area.name}-{gateway}"
                )
                admin_area_level_dict[gateway] = admin_area_level
            admin_area = AdminArea(external_id=external_id,
                                   admin_area_level=admin_area_level,
                                   p_code=properties.get('p_code'),
                                   title = properties.get('name'))
            admin_areas_to_create.append(admin_area)
            admin_areas_external_id_dict[external_id] =admin_area
        #parent assigment
        for location in locations:
            properties = location.get('properties')
            external_id =properties.get('id')
            parent_external_id = properties.get('parent')
            if parent_external_id is None:
                continue
            admin_area = admin_areas_external_id_dict.get(external_id)
            admin_area.parent = admin_areas_external_id_dict.get(parent_external_id)
        AdminArea.objects.bulk_create(admin_areas_to_create)

    def _handle_get_request(self, url, is_absolute_url=False) -> dict:
        if not is_absolute_url:
            url = f"{self._get_url()}{url}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    def _get_paginated_results(self, url) -> list:
        next_url = f"{self._get_url()}{url}"
        results: list = []
        while next_url:
            data = self._handle_get_request(next_url, is_absolute_url=True)
            next_url = data["next"]
            results.extend(data["results"])
        return results

    def _handle_post_request(self, url, data) -> dict:
        response = self._client.post(url=f"{self._get_url()}{url}", data=data)
        response.raise_for_status()
        return response.json()

    def _get_url(self):
        return f"{self.url}/api/v2"


class AdminAreasLoader():
