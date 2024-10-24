import uuid
from typing import Any, List

from django.core.management import call_command
from django.test import override_settings

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import UploadDocumentsBase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceDocumentFactory,
    ReferralTicketWithoutExtrasFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


@override_settings(MEDIA_ROOT=UploadDocumentsBase.TEST_DIR)
class TestGrievanceDocumentsUpload(UploadDocumentsBase):
    CREATE_GRIEVANCE_MUTATION = """
        mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
          createGrievanceTicket(input: $input) {
            grievanceTickets{
              category
              admin
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        cls.update_partner_access_to_program(partner, cls.program)

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

        cls.grievance_data = {
            "description": "Test Feedback",
            "assignedTo": cls.id_to_base64(cls.user.id, "UserNode"),
            "admin": encode_id_base64(str(cls.admin_area.id), "Area"),
            "language": "Polish, English",
        }

        cls.grievance_data_to_create = {
            **cls.grievance_data,
            "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            "consent": True,
            "businessArea": "afghanistan",
        }

        cls.grievance_data_to_update = {
            **cls.grievance_data,
            "ticketId": cls.id_to_base64(cls.ticket_2.ticket.id, "GrievanceTicketNode"),
        }

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_documents(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="scanned_document_1.jpg", size=100, content_type="image/jpeg"
                            ),
                        },
                        {
                            "name": "scanned_document2",
                            "file": self.create_fixture_file(
                                name="scanned_document_2.jpg", size=200, content_type="image/jpeg"
                            ),
                        },
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("some_document.jpg", "image/jpeg"),
            ("some_document.png", "image/png"),
            ("some_document.tiff", "image/tiff"),
            ("some_document.pdf", "application/pdf"),
        ]
    )
    def test_mutation_creates_file_for_allowed_types(self, name: str, content_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD], self.business_area
        )
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(name=name, size=1024, content_type=content_type),
                        }
                    ],
                }
            },
        )

    @parameterized.expand([("some_document.css", "text/css"), ("some_document.html", "text/html")])
    def test_mutation_raises_error_when_not_allowed_type_file_is_uploaded(self, name: str, content_type: str) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD], self.business_area
        )
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(name=name, size=1024, content_type=content_type),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_raises_error_when_uploaded_file_is_bigger_than_3mb(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="some_big_file.jpg", size=5 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD]),
            ("without_permission", []),
        ]
    )
    def test_mutation_raises_error_when_total_size_of_uploaded_files_is_bigger_than_25mb(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_create,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="some_file.jpg", size=2 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                        for _ in range(15)
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_single_document_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "scanned_document1",
                            "file": self.create_fixture_file(
                                name="scanned_document_1.jpg", size=2048, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_updates_single_document_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.maxDiff = None
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(grievance_document.id, "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_deletes_single_document_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToDelete": [self.id_to_base64(grievance_document.id, "GrievanceDocumentNode")],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_and_deletes_documents_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg", size=2048, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToDelete": [self.id_to_base64(grievance_document.id, "GrievanceDocumentNode")],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_and_updates_documents_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg", size=666, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(grievance_document.id, "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_deletes_non_existing_document_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToDelete": [self.id_to_base64(str(uuid.uuid4()), "GrievanceDocumentNode")],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_updates_non_existing_documents_for_existing_grievance_ticket(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(str(uuid.uuid4()), "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_mutation_creates_updates_deletes_documents(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document_to_update = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        grievance_document_to_delete = GrievanceDocumentFactory(
            grievance_ticket=self.ticket_2.ticket, name="this_document_should_be_deleted"
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg", size=666, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(grievance_document_to_update.id, "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToDelete": [
                        self.id_to_base64(grievance_document_to_delete.id, "GrievanceDocumentNode")
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_raises_error_when_mutation_updates_documents_above_25mb_limit(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg", size=3 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(grievance_document.id, "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=30 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_UPDATE]),
            ("without_permission", []),
        ]
    )
    def test_raises_error_when_mutation_updates_document_with_size_5mb(
        self, _: Any, permissions: List[Permissions]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        grievance_document = GrievanceDocumentFactory(grievance_ticket=self.ticket_2.ticket)

        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "input": {
                    **self.grievance_data_to_update,
                    "documentation": [
                        {
                            "name": "created_scanned_document1",
                            "file": self.create_fixture_file(
                                name="created_scanned_document1.jpg", size=3 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                    "documentationToUpdate": [
                        {
                            "id": self.id_to_base64(grievance_document.id, "GrievanceDocumentNode"),
                            "name": "updated_document.jpg",
                            "file": self.create_fixture_file(
                                name="scanned_document_update.jpg", size=5 * 1024 * 1024, content_type="image/jpeg"
                            ),
                        }
                    ],
                }
            },
        )
