from django_countries.fields import Country
from graphql import GraphQLError

from household.models import ROLE_PRIMARY, ROLE_ALTERNATE, IndividualRoleInHousehold, DocumentType, Document


def _handle_role(role, household, individual):
    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        already_existing_role = IndividualRoleInHousehold.objects.filter(household=household, role=role).first()
        if already_existing_role:
            already_existing_role.individual = individual
            already_existing_role.save()
        else:
            IndividualRoleInHousehold.objects.create(individual=individual, household=household, role=role)


def _handle_add_document(document, individual):
    type_name = document.get("type")
    country_code = document.get("country")
    country = Country(country_code)
    number = document.get("number")
    document_type = DocumentType.objects.get(country=country, type=type_name)

    document_already_exists = Document.objects.filter(document_number=number, type=document_type).exists()
    if document_already_exists:
        raise GraphQLError(f"Document with number {number} of type {type_name} for country {country} already exist")

    return Document(document_number=number, individual=individual, type=document_type)
