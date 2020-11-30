def handle_role(role, household, individual):
    from household.models import ROLE_PRIMARY, ROLE_ALTERNATE, IndividualRoleInHousehold

    if role in (ROLE_PRIMARY, ROLE_ALTERNATE) and household:
        already_existing_role = IndividualRoleInHousehold.objects.filter(household=household, role=role).first()
        if already_existing_role:
            already_existing_role.individual = individual
            already_existing_role.save()
        else:
            IndividualRoleInHousehold.objects.create(individual=individual, household=household, role=role)


def handle_add_document(document, individual):
    from django_countries.fields import Country
    from graphql import GraphQLError
    from household.models import DocumentType, Document

    type_name = document.get("type")
    country_code = document.get("country")
    country = Country(country_code)
    number = document.get("number")
    document_type = DocumentType.objects.get(country=country, type=type_name)

    document_already_exists = Document.objects.filter(document_number=number, type=document_type).exists()
    if document_already_exists:
        raise GraphQLError(f"Document with number {number} of type {type_name} for country {country} already exist")

    return Document(document_number=number, individual=individual, type=document_type)


def prepare_previous_documents(documents_to_remove_with_approve_status):
    from django.shortcuts import get_object_or_404
    from core.utils import decode_id_string, encode_id_base64
    from household.models import Document

    previous_documents = {}
    for document_data in documents_to_remove_with_approve_status:

        document_id = decode_id_string(document_data.get("value"))
        document = get_object_or_404(Document, id=document_id)
        previous_documents[encode_id_base64(document.id, "Document")] = {
            "id": encode_id_base64(document.id, "Document"),
            "document_number": document.document_number,
            "individual": encode_id_base64(document.individual.id, "Individual"),
            "label": document.type.label,
            "country": document.type.country.alpha3,
        }

    return previous_documents


def verify_required_arguments(input_data, field_name, options):
    from graphql import GraphQLError
    from core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                raise GraphQLError(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                raise GraphQLError(f"You can't provide {not_allowed} in {key}")


def remove_parsed_data_fields(data_dict, fields_list):
    for field in fields_list:
        data_dict.pop(field, None)
