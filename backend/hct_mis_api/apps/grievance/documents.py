from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from .models import GrievanceTicket, TicketComplaintDetails, TicketSensitiveDetails
from ..household.models import Household
# from hct_mis_api.apps.account.models import User
from ..registration_data.models import RegistrationDataImport
from ..geo.models import Area
from ..core.models import BusinessArea


@registry.register_document
class GrievanceTicketDocument(Document):
    registration_data_import = fields.ObjectField(properties={
        "id": fields.TextField()
    })
    admin2 = fields.ObjectField(properties={
        "id": fields.TextField()
    })
    business_area = fields.ObjectField(properties={
        "slug": fields.KeywordField()
    })
    category = fields.KeywordField(attr="category_to_string")
    status = fields.KeywordField(attr="status_to_string")
    issue_type = fields.KeywordField(attr="issue_type_to_string")
    priority = fields.KeywordField(attr="priority_to_string")
    urgency = fields.KeywordField(attr="urgency_to_string")
    # assigned_to = fields.ObjectField(properties={
    #     "id": fields.KeywordField(),
    #     "username": fields.TextField(),
    # })

    # grievance_type = fields.KeywordField(similarity="boolean")
    # head_of_household_last_name = fields.KeywordField(similarity="boolean")
    # fsp = fields.KeywordField(similarity="boolean")

    # def prepare_assigned_to(self, instance):
    #     if instance.assigned_to:
    #         return instance.assigned_to.id

    # def prepare_grievance_type(self, instance):
    #     return "user" if instance.category in range(2, 8) else "system"
    #
    # def prepare_head_of_household_last_name(self, instance):
    #     household_unicef_id = instance.household_unicef_id
    #     if household_unicef_id:
    #         household = Household.objects.filter(unicef_id=household_unicef_id).first()
    #         return household.head_of_household.family_name
    #
    # def prepare_fsp(self, instance):
    #     if instance.ticket_details:
    #         if isinstance(instance.ticket_details, (TicketComplaintDetails, TicketSensitiveDetails)):
    #             if instance.ticket_details.payment_record:
    #                 return instance.ticket_details.payment_record.service_provider.full_name

    class Django:
        model = GrievanceTicket
        fields = [
            "unicef_id",
            "created_at",
            "household_unicef_id",
        ]
        related_models = [Area, BusinessArea, RegistrationDataImport]

    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}grievance_tickets"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
