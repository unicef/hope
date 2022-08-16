from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.permissions import Permissions


class TestFSPSetup(APITestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.PAYMENT_MODULE_CREATE], BusinessArea.objects.get(slug="afghanistan")
        )

    def test_choosing_delivery_mechanism_order(self):
        # choose some mechanisms
        # see info that selected are not sufficient
        # add remaining
        # approve
        # assign FSPs

        payment_plan = PaymentPlanFactory(total_households_count=1)
        targeting = TargetPopulationFactory()
