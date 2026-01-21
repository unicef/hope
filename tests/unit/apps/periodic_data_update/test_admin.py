from typing import Any
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.periodic_data_update import PDUXlsxTemplateFactory
from hope.apps.account.models import User
from hope.models import PDUXlsxTemplate


class PDUAdminTest(TestCase):
    def setUp(self: Any) -> None:
        self.business_area = create_afghanistan()
        self.admin_user = User.objects.create_superuser(username="root", email="root@root.com", password="password")
        self.client.login(username=self.admin_user.username, password="password")

    @patch("hope.admin.periodic_data_update.export_periodic_data_update_export_template_service.delay")
    def test_post_regenerate_export_xlsx_without_template_post(self, mock_delay: Any) -> None:
        xlsx_template = PDUXlsxTemplateFactory(
            program__business_area=self.business_area,
            business_area=self.business_area,
            status=PDUXlsxTemplate.Status.FAILED,
        )
        url = reverse("admin:periodic_data_update_pduxlsxtemplate_restart_export_task", args=[xlsx_template.pk])

        response = self.client.post(url)
        mock_delay.assert_called_once_with(str(xlsx_template.pk))

        assert response.status_code == 302
        assert (
            reverse(
                "admin:periodic_data_update_pduxlsxtemplate_change",
                args=[xlsx_template.pk],
            )
            in response["Location"]
        )

        # test GET
        response = self.client.get(url)
        assert response.status_code == 200
        assert b"Do you confirm to restart the export task?" in response.content
        assert "admin_extra_buttons/confirm.html" in [t.name for t in response.templates]
