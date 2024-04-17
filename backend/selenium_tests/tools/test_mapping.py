import pytest
pytestmark = pytest.mark.django_db(transaction=True)


class TestMapping:

    @pytest.mark.mapping
    def test_mapping(self) -> None:
        input("Enter")
