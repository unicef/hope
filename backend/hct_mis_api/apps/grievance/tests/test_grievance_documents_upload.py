from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaTypeFactory, AreaFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.geo import models as geo_models


class GrievanceDocumentsUploadTestCase(APITestCase):
    UPLOAD_GRIEVANCE_DOCUMENTS = """
        mutation CreateGrievanceDocumentsMutation(
          $documents: [SupportDocumentInput]
        ) {
            createGrievanceDocumentsMutation(
            documents: $documents
          ) {
                success
            }
        }
    """

    CREATE_GRIEVANCE_MUTATION = """
        mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
          createGrievanceTicket(input: $input) {
            grievanceTickets{
              category
              admin
              language
              description
              consent
              negativeFeedbackTicketDetails {
                household {
                  size
                }
                individual {
                  fullName
                }
              }
            }
          }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)

        call_command("loadcountries")
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asdfgfhghkjltr")

        cls.household, cls.individuals = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )

    def test_user_can_send_one_document(self):
        self.snapshot_graphql_request(
            request_string=self.UPLOAD_GRIEVANCE_DOCUMENTS,
            context={"user": self.user},
            variables={"documents": [
                {
                    "name": "konrad",
                    "file": InMemoryUploadedFile(
                        name="konrad.jpg",
                        file=BytesIO(b"xxxxxxxxxxx"),
                        charset=None,
                        field_name="0",
                        size=100,
                        content_type="image/jpeg"
                    )
                },
                {
                    "name": "konrad2",
                    "file": InMemoryUploadedFile(
                        name="konrad2.jpg",
                        file=BytesIO(b"yyyyyyyyyyyy"),
                        charset=None,
                        field_name="0",
                        size=200,
                        content_type="image/jpeg"
                    )
                }
            ]},
        )

    def test_user_can_send_one_document_other(self):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
                "admin": self.admin_area.p_code,
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan"
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables=input_data
        )
