from django.utils import timezone

from extras.test_utils.factories.account import UserFactory
from factory import SubFactory
from factory.django import DjangoModelFactory

from hope.api.models import APIToken, Grant


class APITokenFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    allowed_ips = ""
    grants = [Grant.API_RDI_CREATE]
    valid_from = timezone.now
    valid_to = None

    class Meta:
        model = APIToken
        django_get_or_create = ("user",)
