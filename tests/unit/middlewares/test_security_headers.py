import importlib

from django.test import Client
from django.test.utils import modify_settings, override_settings
import pytest

from hope.config.env import DEFAULTS

URL = "/_health"

HEADER_TEST_OVERRIDES = {
    "SECURE_CONTENT_TYPE_NOSNIFF": DEFAULTS["SECURE_CONTENT_TYPE_NOSNIFF"][1],
    "SECURE_REFERRER_POLICY": DEFAULTS["SECURE_REFERRER_POLICY"][1],
    "SECURE_HSTS_SECONDS": DEFAULTS["SECURE_HSTS_SECONDS"][1],
    "SECURE_HSTS_INCLUDE_SUBDOMAINS": DEFAULTS["SECURE_HSTS_INCLUDE_SUBDOMAINS"][1],
    "SECURE_HSTS_PRELOAD": DEFAULTS["SECURE_HSTS_PRELOAD"][1],
    "SECURE_SSL_REDIRECT": DEFAULTS["SECURE_SSL_REDIRECT"][1],
}


@pytest.fixture
def anon_client():
    return Client()


@pytest.fixture
def csp_fragment(monkeypatch):
    from hope.config.fragments import csp

    yield csp
    monkeypatch.undo()
    importlib.reload(csp)


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
@pytest.mark.parametrize(
    ("header", "expected"),
    [
        pytest.param("X-Content-Type-Options", "nosniff", id="nosniff"),
        pytest.param("Referrer-Policy", "strict-origin-when-cross-origin", id="referrer-policy"),
        pytest.param("X-Frame-Options", "SAMEORIGIN", id="x-frame-options"),
    ],
)
def test_security_header_value(anon_client, header, expected):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert res.headers[header] == expected


@pytest.mark.django_db
@modify_settings(MIDDLEWARE={"append": "csp.contrib.rate_limiting.RateLimitedCSPMiddleware"})
@override_settings(**HEADER_TEST_OVERRIDES)
def test_content_security_policy(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    csp = res.headers["Content-Security-Policy"]
    assert "default-src" in csp
    assert "object-src 'none'" in csp
    assert "base-uri 'self'" in csp
    assert "frame-ancestors 'self'" in csp
    assert "worker-src 'self' blob:" in csp


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_x_xss_protection_not_set(anon_client):
    res = anon_client.get(URL)
    assert res.status_code == 200
    assert "X-XSS-Protection" not in res.headers


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_hsts_on_secure_request():
    client = Client()
    res = client.get(URL, secure=True)
    assert res.status_code == 200
    sts = res.headers["Strict-Transport-Security"]
    assert "max-age=31536000" in sts
    assert "includeSubDomains" in sts
    assert "preload" in sts


@pytest.mark.django_db
@override_settings(**HEADER_TEST_OVERRIDES)
def test_hsts_behind_tls_terminating_proxy():
    client = Client()
    res = client.get(URL, HTTP_X_FORWARDED_PROTO="https")
    assert res.status_code == 200
    assert "Strict-Transport-Security" in res.headers


def test_csp_report_uri_added_to_directives(monkeypatch, csp_fragment):
    monkeypatch.setenv("CSP_REPORT_URI", "https://report.example.com/csp")

    importlib.reload(csp_fragment)

    assert csp_fragment.CONTENT_SECURITY_POLICY["DIRECTIVES"]["report-uri"] == ("https://report.example.com/csp",)


def test_csp_report_only_uses_report_only_setting(monkeypatch, csp_fragment):
    monkeypatch.setenv("CSP_REPORT_ONLY", "True")
    monkeypatch.setenv("CSP_REPORT_PERCENTAGE", "0.5")

    importlib.reload(csp_fragment)

    assert csp_fragment.CONTENT_SECURITY_POLICY_REPORT_ONLY["REPORT_PERCENTAGE"] == 50.0
    assert csp_fragment.CONTENT_SECURITY_POLICY_REPORT_ONLY["DIRECTIVES"]["frame-src"] == ["'self'"]
