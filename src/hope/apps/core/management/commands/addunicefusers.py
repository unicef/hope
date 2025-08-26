from typing import Any

from django.core.management import BaseCommand

from hope.models.user import User
from hope.models.role_assignment import RoleAssignment
from hope.models.role import Role
from hope.models.business_area import BusinessArea

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
                username=username,
                email=email,
                password="PaymentModule123",
                is_staff=True,
                is_superuser=True,
            )
            RoleAssignment.objects.create(business_area=afg, user=user, role=role)
