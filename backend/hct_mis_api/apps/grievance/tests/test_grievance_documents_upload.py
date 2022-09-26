import base64
import io
import shutil

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import override_settings
from graphene_file_upload.django.testing import GraphQLFileUploadTestCase
from snapshottest.django import TestCase as SnapshotTestTestCase

TEST_DIR = 'test_data'


class MutationTestCase(GraphQLFileUploadTestCase, SnapshotTestTestCase):
    GRAPHQL_URL = "/api/graphql"

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

    @staticmethod
    def id_to_base64(object_id, name):
        return base64.b64encode(f"{name}:{str(object_id)}".encode()).decode()

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

    @classmethod
    def tearDownClass(cls):
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def test_some_mutation(self):

        files = {
            "files.0": InMemoryUploadedFile(
                name="konrad.jpg",
                file=io.BytesIO(b"xxxxxxxxxxx"),
                charset=None,
                field_name="0",
                size=666,
                content_type="image/jpeg"
            ),
            "files.1": InMemoryUploadedFile(
                name="konrad.jpg",
                file=io.BytesIO(b"xxxxxxxxxxx"),
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

        print(response.json())

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
