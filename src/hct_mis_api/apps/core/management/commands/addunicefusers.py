from typing import Any

from django.core.management import BaseCommand

from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.core.models import BusinessArea

emails = [
    "gerba",
    "sapostolico",
    "ddinicola",
    "swaheed",
    "aafaour",
    "asrugano",
    "gkeriri",
    "nmkuzi",
    "trncic",
    "aboncenne",
    "jyablonski",
    "dhassooneh",
]


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        afg = BusinessArea.objects.get(name="Afghanistan")
        role = Role.objects.get(name="Role with all permissions")
        for username in emails:
            email = username + "@unicef.org"
            user = User.objects.create_user(
                username=username, email=email, password="PaymentModule123", is_staff=True, is_superuser=True
            )
            UserRole.objects.create(business_area=afg, user=user, role=role)
