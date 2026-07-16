from hope.contrib.vision import urls


def test_urls_module() -> None:
    assert urls.app_name == "vision"
    assert len(urls.urlpatterns) == 1
    assert urls.urlpatterns[0].name == "payment-plan-callback"
