import os
import base64
import datetime
import json
from pathlib import Path

from graphene.test import Client

from django.core.management import BaseCommand
from django.test import RequestFactory
from django.conf import settings
from django_countries.fields import Country

from hct_mis_api.schema import schema
from hct_mis_api.apps.registration_datahub.celery_tasks import merge_registration_data_import_task
from hct_mis_api.apps.registration_datahub.celery_tasks import (
    automate_rdi_creation_task,
)
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    FlexRegistrationService,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType,
    Record,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.account.models import Role, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.models import BusinessArea


create_grievance_query = """
mutation CreateGrievance($input: CreateGrievanceTicketInput!) {
    createGrievanceTicket(input: $input) {
        grievanceTickets {
        id
        __typename
        }
        __typename
    }
}"""


change_grievance_query = """
mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
  grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
    grievanceTicket {
      id
      status
      createdAt
      updatedAt
      createdBy {
        id
        firstName
        lastName
        username
        email
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

approve_data_change_query = """
mutation ApproveAddIndividualDataChange($grievanceTicketId: ID!, $approveStatus: Boolean!) {
  approveAddIndividual(grievanceTicketId: $grievanceTicketId, approveStatus: $approveStatus) {
    grievanceTicket {
      id
      status
      __typename
    }
    __typename
  }
}
"""


def create_imported_document_types(country_code):
    for document_type_string, _ in FlexRegistrationService.DOCUMENT_MAPPING_TYPE_DICT.items():
        ImportedDocumentType.objects.get_or_create(country=Country(code=country_code), type=document_type_string)


def create_record(registration, status):
    # based on backend/hct_mis_api/apps/registration_datahub/tests/test_extract_records.py
    content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.jpeg").read_bytes()
    fields = {
        "household": [
            {
                "residence_status_h_c": "non_host",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0702001",
                "size_h_c": 5,
            }
        ],
        "individuals": [
            {
                "given_name_i_c": "\u041d\u0430\u0442\u0430\u043b\u0456\u044f",
                "family_name_i_c": "\u0421\u0430\u043f\u0456\u0433\u0430",
                "patronymic": "\u0410\u0434\u0430\u043c\u0456\u0432\u043d\u0430",
                "birth_date": "1983-09-24",
                "gender_i_c": "female",
                "relationship_i_c": "head",
                "disability_i_c": "y",
                "disabiliyt_recognize_i_c": "y",
                "phone_no_i_c": "0636060474",
                "q1": "",
                "tax_id_no_i_c": "123123123",
                "national_id_no_i_c_1": "",
                "international_passport_i_c": "",
                "drivers_license_no_i_c": "",
                "birth_certificate_no_i_c": "",
                "residence_permit_no_i_c": "",
                "role_i_c": "y",
                "bank_account_h_f": "y",
                "bank_name_h_f": "privatbank",
                "other_bank_name": "",
                "bank_account": 2356789789789789,
                "bank_account_number": "879789789",
                "debit_card_number_h_f": 9978967867666,
                "debit_card_number": "87987979789789",
            }
        ],
    }
    files = {
        "individuals": [
            {
                "disability_certificate_picture": str(base64.b64encode(content), "utf-8"),
                "birth_certificate_picture": str(base64.b64encode(content), "utf-8"),
            }
        ],
    }

    return Record.objects.create(
        registration=registration,
        status=status,
        timestamp=datetime.datetime.now(),
        data=None,
        source_id=1,
        fields=fields,
        files=json.dumps(files).encode(),
    )


def create_ua_business_area():
    ukraines = BusinessArea.objects.filter(slug="ukraine")
    if ukraines.exists():
        return ukraines.first()
    return BusinessAreaFactory(slug="ukraine", code="1234", region_name="UA")


def generate_context(user):
    request = RequestFactory()
    context_value = request.get("/api/graphql/")
    context_value.user = user
    return context_value


# TODO: copy pasted, could be in some utils
def create_user_role_with_permissions(user, permissions, business_area):
    permission_list = [perm.value for perm in permissions]
    role, _ = Role.objects.update_or_create(name="Role with Permissions", defaults={"permissions": permission_list})
    user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=business_area)
    return user_role


this_dir = os.path.dirname(os.path.abspath(__file__))
ticket_id_filename = os.path.join(this_dir, "ticket_id.txt")


def create_client():
    return Client(schema)


def initialize_merged_population(command):
    client = create_client()
    create_imported_document_types(country_code="UA")

    registration = 3451234
    amount_of_records = 10

    for _ in range(amount_of_records):
        create_record(registration=registration, status=Record.STATUS_TO_IMPORT)

    previous = set(RegistrationDataImport.objects.all())
    previous_count = len(previous)
    automate_rdi_creation_task(
        registration_id=registration,
        page_size=amount_of_records,
    )
    new = RegistrationDataImport.objects.all()
    new_count = new.count()
    command.stdout.write(f"Created {new_count - previous_count} RDI for {amount_of_records} records")

    set_difference = set(new).difference(previous)
    command.stdout.write(f"Created RDI: {set_difference}")

    previous_individuals = set(Individual.objects.all())

    rdi = next(iter(set_difference))
    merge_registration_data_import_task(rdi.id)
    command.stdout.write(f"Merged RDI: {rdi}")

    new_individuals = set(Individual.objects.all())
    created_individuals = new_individuals.difference(previous_individuals)
    some_individual = next(iter(created_individuals))

    return client, some_individual


def ticket_scenario_till_closed(command, user):
    client, some_individual = initialize_merged_population(command)

    update_variables = {
        "input": {
            "businessArea": "ukraine",
            "description": "descdesc",
            "assignedTo": encode_id_base64(user.pk, "User"),
            "category": 2,
            "consent": True,
            "language": "",
            "area": "",
            "issueType": "14",
            "linkedTickets": [],
            "extras": {
                "issueType": {
                    "individualDataUpdateIssueTypeExtras": {
                        "individual": encode_id_base64(some_individual.pk, "Individual"),
                        "individualData": {"sex": "MALE", "flexFields": {}},
                    }
                }
            },
        }
    }

    update_response = client.execute(
        create_grievance_query,
        variables=update_variables,
        context=generate_context(user=user),
    )

    ticket_id = update_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]
    command.stdout.write(f"Created grievance ticket with id: {ticket_id}")
    proceed_to_close_the_ticket(client, user, command, ticket_id)

    return ticket_id


def proceed_to_close_the_ticket(client, user, command, ticket_id):
    in_progress_variables = {"grievanceTicketId": ticket_id, "status": 3}

    client.execute(
        change_grievance_query,
        variables=in_progress_variables,
        context=generate_context(user=user),
    )
    command.stdout.write("Set grievance ticket to in progress")

    send_for_approval_vars = {
        "grievanceTicketId": ticket_id,
        "status": 5,
    }
    client.execute(
        change_grievance_query,
        variables=send_for_approval_vars,
        context=generate_context(user=user),
    )
    command.stdout.write("Set grievance ticket to sent for approval")

    approve_variables = {
        "grievanceTicketId": ticket_id,
        "approveStatus": True,
    }
    client.execute(
        approve_data_change_query,
        variables=approve_variables,
        context=generate_context(user=user),
    )
    command.stdout.write("Approved data change")

    close_variables = {
        "grievanceTicketId": ticket_id,
        "status": 6,
    }
    client.execute(
        change_grievance_query,
        variables=close_variables,
        context=generate_context(user=user),
    )
    command.stdout.write("Closed grievance ticket")


def create_user_in_business_area_with_permissions(command):
    business_area = create_ua_business_area()
    user = UserFactory(is_superuser=True, is_staff=True)
    create_user_role_with_permissions(
        user,
        [
            Permissions.GRIEVANCES_CREATE,
            Permissions.GRIEVANCES_SET_IN_PROGRESS,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ],
        business_area,
    )
    command.stdout.write(f"Created user {user}")
    return user


class Command(BaseCommand):
    help = "Create, fill and close the grievance ticket, so it triggers deduplication process"

    def handle(self, *args, **options):
        user = create_user_in_business_area_with_permissions(self)
        ticket_scenario_till_closed(self, user)
        # deduplication should be triggered now
