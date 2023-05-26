from django.utils import timezone

from factory import SubFactory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.api.models import APIToken, Grant


class APITokenFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    allowed_ips = ""
    grants = [Grant.API_RDI_CREATE]
    valid_from = timezone.now
    valid_to = None

    class Meta:
        model = APIToken
        django_get_or_create = ("user",)
