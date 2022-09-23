import factory

from ...apps.account.fixtures import UserFactory
from ..models import APIToken


class APITokenFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    allowed_ips = "127.0.0.1, 192.168.66.66"

    class Meta:
        model = APIToken
        django_get_or_create = ("user",)
