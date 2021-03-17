from django.core.management import BaseCommand
from django.db import transaction

from hct_mis_api.apps.account.models import UserPermission


class Command(BaseCommand):
    help = "Generate permissions"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Generate permissions"))
        self._generate_document_types_for_all_countries()

    def _generate_document_types_for_all_countries(self):
        UserPermission.objects.all().delete()
        permissions_to_create = []
        for (permission_name, label) in UserPermission.PERMISSIONS_CHOICES:
            read_permission = UserPermission(name=permission_name)
            write_permission = UserPermission(name=permission_name, write=True)
            permissions_to_create.append(read_permission)
            permissions_to_create.append(write_permission)
        UserPermission.objects.bulk_create(permissions_to_create)
