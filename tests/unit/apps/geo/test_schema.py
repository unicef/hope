from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_ukraine
from hct_mis_api.apps.geo.models import Area, AreaType, Country


class TestSchema(APITestCase):
    maxDiff = None

    QUERY = """
    query AllAreasTree {
      allAreasTree(businessArea: "ukraine") {
        name
        pCode
        level
        areas {
          name
          pCode
          level
          areas {
            name
            pCode
            level
            areas {
              name
              pCode
              level
              areas {
                name
                pCode
                level
              }
            }
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        cls.business_area = create_ukraine()
        country = Country.objects.get(name="Ukraine")
        cls.business_area.countries.add(country)
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
