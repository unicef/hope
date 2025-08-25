from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory

from hope.models.program import Program
from hope.models.universal_update_script import UniversalUpdate


class UniversalUpdateAdminTest(TestCase):
    def setUp(self) -> None:
        User = get_user_model()  # noqa
        self.admin_user = User.objects.create_superuser(username="root", email="root@root.com", password="password")
        self.client.login(username=self.admin_user.username, password="password")
        self.business_area = create_afghanistan()
        self.program = ProgramFactory(
            name="Test Program for Household",
            status=Program.ACTIVE,
            business_area=self.business_area,
        )

    def test_universal_update_admin_edit_page_loads(self) -> None:
        universal_update = UniversalUpdate.objects.create(
            program=self.program,
            individual_fields=["given_name", "family_name"],
        )
        url = reverse(
            "admin:universal_update_script_universalupdate_change",
            args=(universal_update.pk,),
        )
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, "Test Program for Household")
