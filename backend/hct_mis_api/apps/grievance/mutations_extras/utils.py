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


def verify_flex_fields(flex_fields_to_verify, associated_with):
    import re
    from core.core_fields_attributes import FIELD_TYPES_TO_INTERNAL_TYPE, TYPE_SELECT_ONE, TYPE_SELECT_MANY
    from core.utils import serialize_flex_attributes

    if associated_with not in ("households", "individuals"):
        raise ValueError("associated_with argument must be one of ['household', 'individual']")

    all_flex_fields = serialize_flex_attributes().get(associated_with, {})

    for name, value in flex_fields_to_verify.items():
        flex_field = all_flex_fields.get(name)
        if flex_field is None:
            raise ValueError(f"{name} is not a correct `flex field")
        field_type = flex_field["type"]
        field_choices = set(f.get("value") for f in flex_field["choices"])

        if not isinstance(value, FIELD_TYPES_TO_INTERNAL_TYPE[field_type]) or value is None:
            raise ValueError(f"invalid value type for a field {name}")

        if field_type == TYPE_SELECT_ONE and value not in field_choices:
            raise ValueError(f"invalid value: {value} for a field {name}")

        if field_type == TYPE_SELECT_MANY:
            values = set(re.split("[, ;]+", value))
            if values.issubset(field_choices) is False:
                raise ValueError(f"invalid value: {value} for a field {name}")
