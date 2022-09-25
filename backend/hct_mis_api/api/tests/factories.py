from django.utils import timezone

import factory

from ...apps.account.fixtures import UserFactory
from ..models import APIToken, Grant


class APITokenFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    allowed_ips = ""
    grants = [Grant.API_CREATE_RDI]
    valid_from = timezone.now
    valid_to = None

    class Meta:
        model = APIToken
        django_get_or_create = ("user",)
