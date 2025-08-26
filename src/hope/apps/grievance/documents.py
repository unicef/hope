import logging
from typing import Any, Callable, Sequence

from django.conf import settings
from django.db.models import Model, QuerySet
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch import Elasticsearch

from hope.models.user import User
from hope.models.business_area import BusinessArea
from hope.models.area import Area
from hope.apps.grievance.models import GrievanceTicket
from hope.models.household import Household
from hope.models.individual import Individual
from hope.models.document_type import DocumentType
from hope.models.registration_data_import import RegistrationDataImport

logger = logging.getLogger(__name__)

INDEX = f"{settings.ELASTICSEARCH_INDEX_PREFIX}grievance_tickets"


def es_autosync() -> Callable:
    """Check if auto-synchronization with Elasticsearch is turned on [Decorator]."""

    def wrapper(func: Callable) -> Callable:
        def inner(*args: Any, **kwargs: Any) -> Callable | None:
            if settings.ELASTICSEARCH_DSL_AUTOSYNC:
                return func(*args, **kwargs)
            return None

        return inner

    return wrapper


def bulk_update_assigned_to(grievance_tickets_ids: Sequence[str], assigned_to_id: str | None) -> None:
    bulk_update_grievance_ticket_es(grievance_tickets_ids, {"assigned_to": {"id": str(assigned_to_id)}})


def bulk_update_priority(grievance_tickets_ids: Sequence[str], priority: int) -> None:
    bulk_update_grievance_ticket_es(grievance_tickets_ids, {"priority": priority})


def bulk_update_urgency(grievance_tickets_ids: Sequence[str], urgency: int) -> None:
    bulk_update_grievance_ticket_es(grievance_tickets_ids, {"urgency": urgency})


def bulk_update_status(grievance_tickets_ids: Sequence[str], status: int) -> None:
    bulk_update_grievance_ticket_es(grievance_tickets_ids, {"status": status})


@es_autosync()
def bulk_update_grievance_ticket_es(grievance_tickets_ids: Sequence[str], update_query_doc: dict) -> None:
    from elasticsearch.helpers import bulk

    es = Elasticsearch(settings.ELASTICSEARCH_HOST)

    documents_to_update = []
    for ticket_id in grievance_tickets_ids:
        document = {
            "_op_type": "update",
            "_index": INDEX,
            "_id": ticket_id,
            "_source": {"doc": update_query_doc},
        }
        documents_to_update.append(document)
    bulk(es, documents_to_update)
    logger.info(f"GrievanceDocuments with {','.join([str(_id) for _id in grievance_tickets_ids])} have been updated.")


@registry.register_document
class GrievanceTicketDocument(Document):
    unicef_id = fields.KeywordField()
    household_unicef_id = fields.KeywordField()
    registration_data_import = fields.ObjectField(properties={"id": fields.KeywordField()})
    admin2 = fields.ObjectField(properties={"id": fields.KeywordField()})
    business_area = fields.ObjectField(properties={"slug": fields.KeywordField()})
    category = fields.KeywordField(attr="category")
    status = fields.KeywordField(attr="status")
    issue_type = fields.KeywordField(attr="issue_type")
    priority = fields.KeywordField(attr="priority")
    urgency = fields.KeywordField(attr="urgency")
    grievance_type = fields.KeywordField(attr="grievance_type_to_string")
    assigned_to = fields.ObjectField(properties={"id": fields.KeywordField()})
    ticket_details = fields.ObjectField(
        properties={
            "household": fields.ObjectField(
                properties={
                    "head_of_household": fields.ObjectField(
                        properties={
                            "family_name": fields.KeywordField(),
                            "documents": fields.ListField(
                                fields.ObjectField(
                                    properties={
                                        "number": fields.KeywordField(attr="document_number"),
                                        "type": fields.KeywordField(attr="type.key"),
                                    }
                                )
                            ),
                        }
                    )
                }
            )
        }
    )
    programs = fields.ListField(fields.KeywordField())

    class Django:
        model = GrievanceTicket
        fields = [
            "created_at",
        ]
        related_models = [
            Area,
            BusinessArea,
            Household,
            Individual,
            Document,
            DocumentType,
            RegistrationDataImport,
            User,
        ]

    class Index:
        name = INDEX
        settings = settings.ELASTICSEARCH_BASE_SETTINGS

    def get_instances_from_related(self, related_instance: Model) -> QuerySet:
        if isinstance(related_instance, BusinessArea):
            return related_instance.tickets.all()
        return GrievanceTicket.objects.none()

    def prepare_programs(self, instance: GrievanceTicket) -> list[str]:
        return list(instance.programs.values_list("id", flat=True))
