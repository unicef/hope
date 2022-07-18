from django.core.management import BaseCommand

from hct_mis_api.apps.registration_datahub.management.commands.trigger_deduplication import (
    initialize_merged_population,
    create_user_in_business_area_with_permissions,
    encode_id_base64,
    create_grievance_query,
    generate_context,
    proceed_to_close_the_ticket,
)


def update_household_ticket_scenario_till_closed(command, user):
    client, some_individual = initialize_merged_population(command)

    create_variables = {
        "input": {
            "businessArea": "ukraine",
            "description": "12341234",
            "assignedTo": encode_id_base64(user.pk, "User"),
            "category": 2,
            "consent": True,
            "language": "",
            "area": "",
            "issueType": "13",
            "linkedTickets": [],
            "extras": {
                "issueType": {
                    "householdDataUpdateIssueTypeExtras": {
                        "household": encode_id_base64(some_individual.household.pk, "Household"),
                        "householdData": {"maleAgeGroup05Count": 1, "flexFields": {}},
                    }
                }
            },
        }
    }

    create_response = client.execute(
        create_grievance_query,
        variables=create_variables,
        context=generate_context(user=user),
    )
    ticket_id = create_response["data"]["createGrievanceTicket"]["grievanceTickets"][0]["id"]

    proceed_to_close_the_ticket(client, user, command, ticket_id)


class Command(BaseCommand):
    help = "Create, fill and close the 'needs adjudication' ticket"

    def handle(self, *args, **options):
        user = create_user_in_business_area_with_permissions(self)
        update_household_ticket_scenario_till_closed(self, user)
        # should trigger locking individual's table
