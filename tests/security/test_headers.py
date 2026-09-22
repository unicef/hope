from django.test import Client
from django.test.utils import override_settings
import pytest

URL = "/"

HEADER_TEST_OVERRIDES = {
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    "SECURE_REFERRER_POLICY": "strict-origin-when-cross-origin",
    "SECURE_SSL_REDIRECT": False,
}


@pytest.fixture
def anon_client():
    return Client()


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_content_type_options_nosniff(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert res.headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_referrer_policy(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_x_frame_options_sameorigin(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert res.headers["X-Frame-Options"] == "SAMEORIGIN"


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_content_security_policy(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    csp = res.headers["Content-Security-Policy"]
    assert "default-src" in csp
    assert "object-src 'none'" in csp
    assert "base-uri 'self'" in csp


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_x_xss_protection_not_set(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert "X-XSS-Protection" not in res.headers


@pytest.mark.django_db
@override_settings(
    SECURE_HSTS_SECONDS=31536000,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
    SECURE_HSTS_PRELOAD=True,
    SECURE_SSL_REDIRECT=False,
)
def test_hsts_on_secure_request():
    client = Client()
    res = client.get(URL, secure=True)
    assert res.status_code == 200
    sts = res.headers["Strict-Transport-Security"]
    assert "max-age=31536000" in sts
    assert "includeSubDomains" in sts
    assert "preload" in sts


@pytest.mark.django_db
@override_settings(
    SECURE_HSTS_SECONDS=31536000,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
    SECURE_HSTS_PRELOAD=False,
    SECURE_SSL_REDIRECT=False,
)
def test_hsts_min_lifetime_one_year():
    client = Client()
    res = client.get(URL, secure=True)
    assert res.status_code == 200
    sts = res.headers["Strict-Transport-Security"]
    assert "max-age=31536000" in sts


@pytest.mark.django_db
@override_settings(
    SECURE_HSTS_SECONDS=31536000,
    SECURE_SSL_REDIRECT=False,
)
def test_hsts_behind_tls_terminating_proxy():
    client = Client()
    res = client.get(URL, HTTP_X_FORWARDED_PROTO="https")
    assert res.status_code == 200
    assert "Strict-Transport-Security" in res.headers
