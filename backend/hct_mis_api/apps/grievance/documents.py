from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from .models import GrievanceTicket
from ..household.models import Household


@registry.register_document
class GrievanceTicketDocument(Document):
    created_at = fields.DateField(similarity="boolean")
    assigned_to = fields.TextField()
    registration_data_import = fields.TextField()
    status = fields.TextField()
    issue_type = fields.TextField()
    category = fields.TextField()
    admin = fields.TextField()
    priority = fields.TextField()
    urgency = fields.TextField()
    grievance_type = fields.KeywordField(similarity="boolean")
    head_of_household_last_name = fields.KeywordField(similarity="boolean")
    business_area = fields.KeywordField(similarity="boolean")

    def prepare_assigned_to(self, instance):
        if instance.assigned_to:
            return instance.assigned_to.id

    def prepare_registration_data_import(self, instance):
        if instance.registration_data_import:
            return instance.registration_data_import.id

    def prepare_admin2_new(self, instance):
        if instance.admin2_new:
            return instance.admin2_new.id

    def prepare_grievance_type(self, instance):
        return "user" if instance.category in range(2, 8) else "system"

    def prepare_head_of_household_last_name(self, instance):
        household_unicef_id = instance.household_unicef_id
        if household_unicef_id:
            household = Household.objects.filter(unicef_id=household_unicef_id).first()
            return household.head_of_household.family_name

    def prepare_business_area(self, instance):
        return instance.business_area.slug

    class Django:
        model = GrievanceTicket
        fields = []

    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}grievance_tickets"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
