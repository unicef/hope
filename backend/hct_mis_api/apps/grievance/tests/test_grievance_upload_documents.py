import uuid

from django.core.management import call_command
from django.test import override_settings
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import UploadDocumentsBase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import ReferralTicketWithoutExtrasFactory, GrievanceDocumentFactory
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household


@override_settings(MEDIA_ROOT=UploadDocumentsBase.TEST_DIR)
class TestGrievanceDocumentsUpload(UploadDocumentsBase):
    CREATE_GRIEVANCE_MUTATION = """
        mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
          createGrievanceTicket(input: $input) {
            grievanceTickets{
              category
              admin
              language
              description
              consent
              documentation {
                name
                fileSize
                contentType
              }
            }
          }
        }
        """

    UPDATE_GRIEVANCE_MUTATION = """
        mutation UpdateGrievanceTicket(
          $input: UpdateGrievanceTicketInput!
        ) {
          updateGrievanceTicket(input: $input) {
            grievanceTicket{
              category
              admin
              language
              description
              consent
              documentation {
                name
                fileSize
                contentType
              }
            }
          }
        }
        """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
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

        cls.ticket = ReferralTicketWithoutExtrasFactory()
        cls.ticket.ticket.status = GrievanceTicket.STATUS_NEW
        cls.ticket.ticket.save()

        cls.ticket_2 = ReferralTicketWithoutExtrasFactory()
        cls.ticket_2.ticket.status = GrievanceTicket.STATUS_NEW
        cls.ticket_2.ticket.save()

        cls.grievance_document = GrievanceDocumentFactory(grievance_ticket=cls.ticket_2.ticket)

        cls.grievance_data = {
            "description": "Test Feedback",
            "assignedTo": cls.id_to_base64(cls.user.id, "UserNode"),
            "admin": cls.admin_area.p_code,
            "language": "Polish, English"
        }

        cls.grievance_data_to_create = {
            **cls.grievance_data,
            "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            "consent": True,
            "businessArea": "afghanistan"
        }

        cls.grievance_data_to_update = {
            **cls.grievance_data,
            "ticketId": cls.id_to_base64(cls.ticket_2.ticket.id, "GrievanceTicketNode")
        }

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_documents(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="scanned_document_1.jpg",
                                size=100,
                                content_type="image/jpeg"
                            )
                        },
                        {
                            "name": "scanned_document2",
                            "file": self.create_fixture_file(
                                name="scanned_document_2.jpg",
                                size=200,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand([
        ("some_document.jpg", "image/jpeg"),
        ("some_document.png", "image/png"),
        ("some_document.tiff", "image/tiff"),
        ("some_document.pdf", "application/pdf")
    ])
    def test_mutation_creates_file_for_allowed_types(self, name, content_type):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD], self.business_area
        )
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name=name,
                                size=1024,
                                content_type=content_type
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand([
        ("some_document.css", "text/css"),
        ("some_document.html", "text/html")
    ])
    def test_mutation_raises_error_when_not_allowed_type_file_is_uploaded(self, name, content_type):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD], self.business_area
        )
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name=name,
                                size=1024,
                                content_type=content_type
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_raises_error_when_uploaded_file_is_bigger_than_3mb(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="some_big_file.jpg",
                                size=5 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_raises_error_when_total_size_of_uploaded_files_is_bigger_than_25mb(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="some_file.jpg",
                                size=2 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                        for _ in range(15)
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_single_document_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="scanned_document_1.jpg",
                                size=2048,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_updates_single_document_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToUpdate": [
                        {
                            "id": self.grievance_document.id,
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_deletes_single_document_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToDelete": [self.grievance_document.id]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_and_deletes_documents_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg",
                                size=2048,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToDelete": [self.grievance_document.id]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_and_updates_documents_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg",
                                size=666,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.grievance_document.id,
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_deletes_non_existing_document_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToDelete": [uuid.uuid4()]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_updates_non_existing_documents_for_existing_grievance_ticket(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToUpdate": [
                        {
                            "id": uuid.uuid4(),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_updates_deletes_documents(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        grievance_document_to_delete = GrievanceDocumentFactory(
            grievance_ticket=self.ticket_2.ticket,
            name="this_document_should_be_deleted"
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg",
                                size=666,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.grievance_document.id,
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToDelete": [grievance_document_to_delete.id]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_raises_error_when_mutation_updates_documents_above_25mb_limit(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg",
                                size=3 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.grievance_document.id,
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=30 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_raises_error_when_mutation_updates_document_with_size_5mb(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg",
                                size=3 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.grievance_document.id,
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg",
                                size=5 * 1024 * 1024,
                                content_type="image/jpeg"
                            )
                        }
                    ]
                }
            }
        )
