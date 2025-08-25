from typing import TYPE_CHECKING

from django.urls import reverse

if TYPE_CHECKING:
    pass


def test_template_file(django_app: "DjangoTestApp", admin_user: "User") -> None:
    url = reverse("sanction:download_sanction_template")
    res = django_app.get(url, user=admin_user)
    assert res.status_code == 200
