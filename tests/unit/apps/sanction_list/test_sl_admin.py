from django.urls import reverse
import responses


def test_sanction_list_refresh(
    django_app: "DjangoTestApp",
    admin_user: "User",
    sanction_list: "SanctionList",
    eu_file: str,
    mocked_responses: "RequestsMock",
) -> None:
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    url = reverse("admin:sanction_list_sanctionlist_change", args=(sanction_list.id,))
    res = django_app.get(url, user=admin_user)
    res = res.click("Refresh")
    assert res.status_code == 302


def test_sanction_list_empty(
    django_app: "DjangoTestApp",
    admin_user: "User",
    sanction_list: "SanctionList",
    mocked_responses: "RequestsMock",
) -> None:
    url = reverse("admin:sanction_list_sanctionlist_change", args=(sanction_list.id,))
    res = django_app.get(url, user=admin_user)
    res = res.click("Empty")
    assert res.status_code == 200
    res = res.form.submit()
    assert res.status_code == 302
