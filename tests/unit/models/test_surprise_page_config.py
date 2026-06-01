import pytest

from extras.test_utils.factories.core import SurprisePageConfigFactory
from hope.models.surprise_page_config import SurprisePageConfig

pytestmark = pytest.mark.django_db


def test_str_returns_special_page_configuration() -> None:
    config = SurprisePageConfigFactory()
    assert str(config) == "Special Page Configuration"


def test_save_forces_pk_1() -> None:
    config = SurprisePageConfigFactory()
    assert config.pk == 1


def test_save_is_singleton() -> None:
    first = SurprisePageConfigFactory(heading="First")
    second = SurprisePageConfigFactory(heading="Second")
    assert first.pk == second.pk == 1
    assert SurprisePageConfig.objects.count() == 1
    assert SurprisePageConfig.objects.get(pk=1).heading == "Second"


def test_delete_does_not_remove_record() -> None:
    config = SurprisePageConfigFactory()
    result = config.delete()
    assert result == (0, {})
    assert SurprisePageConfig.objects.filter(pk=1).exists()


def test_defaults() -> None:
    config = SurprisePageConfig()
    config.save()
    assert config.heading == "🎉 You found a secret!"
    assert config.subheading == "Congratulations, explorer."
    assert not config.image
