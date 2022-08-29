from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.core.models import BusinessArea

from .models import GrievanceTicket


@registry.register_document
class GrievanceTicketDocument(Document):
    unicef_id = fields.KeywordField()
    household_unicef_id = fields.KeywordField()
    registration_data_import = fields.ObjectField(properties={
        "id": fields.KeywordField()
    })
    admin2 = fields.ObjectField(properties={
        "id": fields.KeywordField()
    })
    business_area = fields.ObjectField(properties={
        "slug": fields.KeywordField()
    })
    category = fields.KeywordField(attr="category_to_string")
    status = fields.KeywordField(attr="status_to_string")
    issue_type = fields.KeywordField(attr="issue_type_to_string")
    priority = fields.KeywordField(attr="priority_to_string")
    urgency = fields.KeywordField(attr="urgency_to_string")
    grievance_type = fields.KeywordField(attr="grievance_type_to_string")
    assigned_to = fields.ObjectField(properties={
        "id": fields.KeywordField()
    })
    ticket_details = fields.ObjectField(
        properties={
            "household": fields.ObjectField(
                properties={
                    "head_of_household": fields.ObjectField(properties={
                        "family_name": fields.KeywordField()
                    })
                }
            )
        }
    )

    class Django:
        model = GrievanceTicket
        fields = [
            "created_at",
        ]
        related_models = [Area, BusinessArea, Household, Individual, RegistrationDataImport, User]

    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}grievance_tickets"
        settings = settings.ELASTICSEARCH_BASE_SETTINGS

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, BusinessArea):
            return related_instance.tickets.all()
