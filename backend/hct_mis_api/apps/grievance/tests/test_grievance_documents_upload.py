from django.test import override_settings

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import BaseMultipleFilesUploadTestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory


@override_settings(MEDIA_ROOT=(BaseMultipleFilesUploadTestCase.TEST_DIR + '/media'))
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

    def test_user_can_send_one_document(self):
        response = self.file_query(
            query=self.UPLOAD_GRIEVANCE_DOCUMENTS,
            op_name="uploadDocuments",
            files={
                "files.0": self.create_fixture_file(
                    name="some_file.jpg",
                    size=100,
                    content_type="image/jpeg"
                )
            },
            variables={
                "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
                "files": [None]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'data': {
                    'uploadDocuments': {
                        'success': True
                    },
                }
            }
        )

        self.assertMatchSnapshot(response.json())

    def test_user_can_send_multiple_documents(self):
        response = self.file_query(
            query=self.UPLOAD_GRIEVANCE_DOCUMENTS,
            op_name="uploadDocuments",
            files={
                "files.0": self.create_fixture_file(
                    name="some_file.jpg",
                    size=100,
                    content_type="image/jpeg"
                ),
                "files.1": self.create_fixture_file(
                    name="some_file.png",
                    size=200,
                    content_type="image/png"
                ),
                "files.2": self.create_fixture_file(
                    name="some_file.pdf",
                    size=300,
                    content_type="application/pdf"
                )
            },
            variables={
                "grievanceTicketId": self.id_to_base64(self.grievance_ticket.id, "GrievanceTicketNode"),
                "files": [None, None, None]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'data': {
                    'uploadDocuments': {
                        'success': True
                    },
                }
            }
        )

        self.assertMatchSnapshot(response.json())
