from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_ukraine
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.geo.models import Area, AreaType, Country


class TestSchema(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        cls.business_area = create_ukraine()
        country = Country.objects.get(name="Ukraine")
        cls.business_area.countries.add(country)

        p_code_prefix = country.iso_code2
        area_type_level_1 = AreaType.objects.get(country=country, area_level=1)
        area_type_level_2 = area_type_level_1.get_children().first()
        area_type_level_3 = area_type_level_2.get_children().first()
        area_type_level_4 = area_type_level_3.get_children().first()
        area_type_level_5 = area_type_level_4.get_children().first()
        # 1 level
        area_l_1 = AreaFactory(area_type=area_type_level_1, p_code=f"{p_code_prefix}11", name="City1")
        area_l_2 = AreaFactory(
            area_type=area_type_level_2, p_code=f"{p_code_prefix}1122", parent=area_l_1, name="City2"
        )
        area_l_3 = AreaFactory(
            area_type=area_type_level_3, p_code=f"{p_code_prefix}112233", parent=area_l_2, name="City3"
        )
        area_l_4 = AreaFactory(
            area_type=area_type_level_4, p_code=f"{p_code_prefix}11223344", parent=area_l_3, name="City4"
        )
        AreaFactory(area_type=area_type_level_5, p_code=f"{p_code_prefix}1122334455", parent=area_l_4, name="City5")

        Area.objects.rebuild()
        AreaType.objects.rebuild()
        Country.objects.rebuild()
        cls.user = UserFactory.create(first_name="John", last_name="Doe")

    def test_get_areas_tree(self) -> None:
        with self.assertNumQueries(2):
            self.snapshot_graphql_request(
                request_string=self.QUERY,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                    },
                },
            )
