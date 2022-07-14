from parameterized import parameterized

from hct_mis_api.apps.payment.models import ApprovalProcess
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household


class TestCreateAcceptanceProcessMutation(APITestCase):
    MUTATION = """
        mutation createAcceptanceProcess( $input: CreateAcceptanceProcessInput! ) {
            createAcceptanceProcess(input: $input) {
                acceptanceProcess{
                    approvals{
                        stage
                        objs{
                            stage
                            type
                            info
                            comment
                        }
                    }
                }
            }
        }
    """
    stage_and_approval_type = {
        0: ["invalid", "APPROVAL", "AUTHORIZATION", "FINANCE_REVIEW", "REJECT", "REJECT"],
        1: [
            "APPROVAL",
            "APPROVAL",
            "APPROVAL",
            "AUTHORIZATION",
            "FINANCE_REVIEW",
            "AUTHORIZATION",
            "FINANCE_REVIEW",
            "FINANCE_REVIEW",
            "FINANCE_REVIEW",
            "REJECT",
        ],
        2: ["APPROVAL"],
        99: ["APPROVAL"],
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(first_name="Rachel", last_name="Walker")
        create_afghanistan()  # approval 2, authorization 2, fin_review 3
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        # cls.payment_plan = PaymentPlanFactory.create(business_area=cls.business_area)
        cls.payment_plan = ApprovalProcess.objects.create(
            approved_by=cls.user,
            approve_date="2022-03-03",
        )

    @parameterized.expand(
        [
            # ("with_permission", [Permissions.PAYMENT_MODULE_CREATE], stage_and_approval_type),
            ("without_permission", [], stage_and_approval_type),  # {0: ["APPROVAL"]}
        ]
    )
    def test_create_acceptance_process(self, _, permissions, stage_and_approval_type):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        # TODO: will update

        # for stage, types in stage_and_approval_type.items():
        #     for ap_type in types:
        #         self.snapshot_graphql_request(
        #             request_string=self.MUTATION,
        #             context={"user": self.user},
        #             variables={
        #                 "input": {
        #                     "paymentPlanId": self.payment_plan.id,
        #                     "stage": stage,
        #                     "acceptanceProcessType": ap_type,
        #                     "comment": f"default comment for {stage} and type {ap_type}",
        #                 }
        #             },
        #         )
