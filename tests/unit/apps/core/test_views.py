from django.urls import reverse


def test_base_hope_template_get(client):
    url = reverse("base-hope-template-view")
    response = client.get(url)
    assert response.status_code == 200
    assert "example_extended_template.html" in [t.name for t in response.templates]
