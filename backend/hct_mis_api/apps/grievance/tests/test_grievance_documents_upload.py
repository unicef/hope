from io import BytesIO

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import BaseMultipleFilesUploadTestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import override_settings


class SupportGrievanceTicketDocumentsUploadTestCase(BaseMultipleFilesUploadTestCase):
    UPLOAD_GRIEVANCE_DOCUMENTS = """
        mutation uploadDocuments(
          $files: [Upload]!
          $grievanceTicketId: ID!
        ) {
            uploadDocuments(
            files: $files, 
            grievanceTicketId: $grievanceTicketId
          ) {
                success
            }
        }
    """

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        create_afghanistan()
        cls.business_area_slug = "afghanistan"
        cls.business_area = BusinessArea.objects.get(slug=cls.business_area_slug)

        cls.grievance_ticket = GrievanceTicketFactory(
            created_by=cls.user,
            assigned_to=cls.user
        )

    @override_settings(MEDIA_ROOT=(BaseMultipleFilesUploadTestCase.TEST_DIR + '/media'))
    def test_some_mutation(self):

        files = {
            "files.0": InMemoryUploadedFile(
                name="konrad.jpg",
                file=BytesIO(b"xxxxxxxxxxx"),
                charset=None,
                field_name="0",
                size=666,
                content_type="image/jpeg"
            ),
            "files.1": InMemoryUploadedFile(
                name="konrad.jpg",
                file=BytesIO(b"yyyyyyyyyyy"),
                charset=None,
                field_name="0",
                size=666,
                content_type="image/jpeg"
            )
        }

        response = self.file_query(
            query=self.UPLOAD_GRIEVANCE_DOCUMENTS,
            op_name="uploadDocuments",
            files=files,
            variables={
                "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
                "files": [None, None]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "data": {
                    "uploadDocuments": {
                        "success": True
                    }
                }
            }
        )

        self.assertMatchSnapshot(response.json())
