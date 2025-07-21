from typing import Any, List

from django.core.management import call_command

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.household import create_household
from tests.extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory


class TestGrievanceCreateSensitiveTicketQuery(APITestCase):
    CREATE_GRIEVANCE_MUTATION = """
    mutation CreateGrievanceTicket($input: CreateGrievanceTicketInput!) {
      createGrievanceTicket(input: $input) {
        grievanceTickets{
          category
          issueType
          admin
          language
          description
          consent
          sensitiveTicketDetails {
            household {
              size
            }
            individual {
              fullName
            }
            paymentRecord {
              fullName
            }
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

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area = AreaFactory(name="City Test", area_type=area_type, p_code="asfdsfg")

        cls.household1, cls.individuals1 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe"},
        )
        cls.household2, cls.individuals2 = create_household(
            {"size": 1, "business_area": cls.business_area},
            {"given_name": "John", "family_name": "Doe", "middle_name": "", "full_name": "John Doe Second Individual"},
        )
        cls.program = ProgramFactory(status=Program.ACTIVE, business_area=cls.business_area)
        payment_plan = PaymentPlanFactory(program_cycle=cls.program.cycles.first(), business_area=cls.business_area)
        cls.payment = PaymentFactory(
            household=cls.household1,
            collector=cls.individuals1[0],
            business_area=cls.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        cls.second_payment = PaymentFactory(
            household=cls.household2,
            collector=cls.individuals2[0],
            business_area=cls.business_area,
            parent=payment_plan,
            currency="PLN",
        )
        cls.update_partner_access_to_program(partner, cls.program)
        cls.maxDiff = None

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_wrong_extras(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "grievanceComplaintTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_without_issue_type(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode"),
                            "paymentRecord": [self.id_to_base64(self.payment.id, "PaymentNode")],
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_with_two_payment_records(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode"),
                            "paymentRecord": [
                                self.id_to_base64(self.payment.id, "PaymentNode"),
                                self.id_to_base64(self.second_payment.id, "PaymentNode"),
                            ],
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_without_payment_record(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode"),
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode"),
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_without_household(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "individual": self.id_to_base64(self.individuals1[0].id, "IndividualNode")
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_without_individual(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
                "extras": {
                    "category": {
                        "sensitiveGrievanceTicketExtras": {
                            "household": self.id_to_base64(self.household1.id, "HouseholdNode")
                        }
                    }
                },
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_CREATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_create_sensitive_ticket_without_extras(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "Test Feedback",
                "assignedTo": self.id_to_base64(self.user.id, "UserNode"),
                "category": GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
                "issueType": GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS,
                "admin": encode_id_base64(str(self.admin_area.id), "Area"),
                "language": "Polish, English",
                "consent": True,
                "businessArea": "afghanistan",
            }
        }

        self.snapshot_graphql_request(
            request_string=self.CREATE_GRIEVANCE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
