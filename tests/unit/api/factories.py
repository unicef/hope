from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory

from extras.test_utils.factories.account import UserFactory
from hope.models import APIToken
from hope.models.utils import Grant


class APITokenFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    allowed_ips = ""
    grants = [Grant.API_RDI_CREATE]
    valid_from = timezone.now
    valid_to = None

    class Meta:
        model = APIToken
        django_get_or_create = ("user",)
