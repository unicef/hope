from unittest import mock

from dateutil.parser import parse

from account.fixtures import UserFactory
from core.base_test_case import APITestCase


class TestKoboProjectsQuery(APITestCase):
    ALL_KOBO_PROJECTS = """
    query AllKoboProjects {
      allKoboProjects {
        totalCount
            edges {
              node {
                uid
                country
                xlsLink
                hasDeployment
                deploymentActive
                name
                dateModified
              }
        }
      }
    }
    """

    SINGLE_KOBO_PROJECT = """
    query koboProject {
      koboProject(uid: "a7rujYsuzrMo7PJtriSfqK") {
        uid
        country
        xlsLink
        hasDeployment
        deploymentActive
        name
        dateModified
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    @mock.patch(
        "core.schema.reduce_assets_list",
        new=lambda assets, only_deployed: [
            {
                "uid": "a7rujYsuzrMo7PJtriSfqK",
                "country": "Afghanistan",
                "xls_link": "https://kobo.humanitarianresponse.info/api/v2/"
                "assets/a7rujYsuzrMo7PJtriSfqK/?format=json.xls",
                "has_deployment": False,
                "deployment_active": False,
                "name": "cloned test",
                "date_modified": parse("2020-05-20T10:44:19.596582+00:00"),
            },
            {
                "uid": "aNZohcKTvCTg2tRpKGYC4E",
                "country": "Afghanistan",
                "xls_link": "https://kobo.humanitarianresponse.info/api/v2/"
                "assets/aNZohcKTvCTg2tRpKGYC4E/?format=json.xls",
                "has_deployment": False,
                "deployment_active": False,
                "name": "cloned test",
                "date_modified": parse("2020-05-20T10:44:19.417452+00:00"),
            },
        ],
    )
    def test_all_kobo_projects_query(self):
        self.snapshot_graphql_request(
            request_string=self.ALL_KOBO_PROJECTS, context={"user": self.user},
        )

    @mock.patch(
        "core.schema.reduce_asset",
        new=lambda asset: {
            "uid": "a7rujYsuzrMo7PJtriSfqK",
            "country": "Afghanistan",
            "xls_link": "https://kobo.humanitarianresponse.info/api/v2/"
            "assets/a7rujYsuzrMo7PJtriSfqK/?format=json.xls",
            "has_deployment": False,
            "deployment_active": False,
            "name": "cloned test",
            "date_modified": parse("2020-05-20T10:44:19.596582+00:00"),
        },
    )
    def test_single_kobo_project_query(self):
        self.snapshot_graphql_request(
            request_string=self.SINGLE_KOBO_PROJECT,
            context={"user": self.user},
        )
