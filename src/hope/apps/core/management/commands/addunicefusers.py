from typing import Any

from django.core.management import BaseCommand

from hope.models.business_area import BusinessArea
from hope.models.role import Role
from hope.models.role_assignment import RoleAssignment
from hope.models.user import User

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
            user = User.objects.create_user(username=username, email=email, is_staff=True, is_superuser=True)
            user.set_unusable_password()
            user.save()
            RoleAssignment.objects.create(business_area=afg, user=user, role=role)
