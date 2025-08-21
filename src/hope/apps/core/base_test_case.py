import base64
import os
import random
import shutil
import time
from contextlib import suppress
from functools import reduce
from io import BytesIO
from typing import TYPE_CHECKING, Any, Iterable, Optional

import factory
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.program import ProgramFactory
from snapshottest.django import TestCase as SnapshotTestTestCase

from hope.apps.account.models import AdminAreaLimitedTo, Role, RoleAssignment
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.models import IDENTIFICATION_TYPE_CHOICE, DocumentType

if TYPE_CHECKING:  # pragma: no_cover
    from hope.apps.account.models import Partner, User
    from hope.apps.core.models import BusinessArea
    from hope.apps.geo.models import Area
    from hope.apps.program.models import Program


class BaseTestCase:

    @classmethod
    def generate_document_types_for_all_countries(cls) -> None:
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))

        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

    @staticmethod
    def set_admin_area_limits_in_program(
        partner: "Partner",
        program: "Program",
        areas: list["Area"],
    ) -> None:
        admin_area_limits, _ = AdminAreaLimitedTo.objects.get_or_create(
            program=program,
            partner=partner,
        )
        admin_area_limits.areas.set(areas)

    @classmethod
    def create_partner_role_with_permissions(
        cls,
        partner: "Partner",
        permissions: Iterable,
        business_area: "BusinessArea",
        program: Optional["Program"] = None,
        areas: list["Area"] | None = None,
        name: str | None = None,
        whole_business_area_access: bool | None = False,
    ) -> RoleAssignment:
        """Create Partner Role with permissions.

        whole_business_area_access: If True, the role is created for all programs in a business area (program=None).
        """
        permission_list = [perm.value for perm in permissions]
        name = name or f"Partner Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for Partner Role")
        partner.allowed_business_areas.add(business_area)
        role_assignment, _ = RoleAssignment.objects.get_or_create(
            partner=partner, role=role, business_area=business_area, program=program
        )
        # not admin area limits in program
        if program and areas:
            cls.set_admin_area_limits_in_program(partner, program, areas)
        return role_assignment

    @classmethod
    def create_user_role_with_permissions(
        cls,
        user: "User",
        permissions: Iterable,
        business_area: "BusinessArea",
        program: Optional["Program"] = None,
        areas: list["Area"] | None = None,
        name: str | None = None,
        whole_business_area_access: bool | None = False,
    ) -> RoleAssignment:
        """Create User Role with related permissions.

        whole_business_area_access: If True, the role is created for all programs in a business area (program=None).
        """
        permission_list = [perm.value for perm in permissions]
        name = name or f"User Role with Permissions {permission_list[0:3], ...}"
        role, created = Role.objects.update_or_create(name=name, defaults={"permissions": permission_list})
        # whole_business_area is used to create a role for all programs in a business area (program=None)
        if not program and not whole_business_area_access:
            program = ProgramFactory(business_area=business_area, name="Program for User Role")
        role_assignment, _ = RoleAssignment.objects.get_or_create(
            user=user, role=role, business_area=business_area, program=program
        )

        # set admin area limits in program
        if program and areas:
            cls.set_admin_area_limits_in_program(user.partner, program, areas)
        return role_assignment
