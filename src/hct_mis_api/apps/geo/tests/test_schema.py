from django.conf import settings

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area, AreaType, Country


class TestSchema(APITestCase):
    maxDiff = None
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    QUERY = """
    query AllAreasTree {
      allAreasTree(businessArea: "afghanistan") {
        name
        pCode
        areas {
          name
          pCode
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()
        country = Country.objects.get(name="Afghanistan")
        cls.business_area.countries.add(country)
        Area.objects.rebuild()
        AreaType.objects.rebuild()
        Country.objects.rebuild()
        cls.user = UserFactory.create(first_name="John", last_name="Doe")

    def test_get_areas_tree(self) -> None:
        with self.assertNumQueries(1):
            self.snapshot_graphql_request(
                request_string=self.QUERY,
                context={
                    "user": self.user,
                    "headers": {
                        "Business-Area": self.business_area.slug,
                    },
                },
            )
