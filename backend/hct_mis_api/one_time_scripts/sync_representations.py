import copy
import logging
import os
from typing import Any, List, Tuple, Union

from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q, QuerySet
from django.db.models.fields.files import ImageFieldFile

from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage, Message
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    GrievanceTicketThrough,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import HouseholdSelection
from hct_mis_api.one_time_scripts.migrate_data_for_sync import (
    copy_bank_account_info_per_individual_fast,
    copy_document_per_individual_fast,
    copy_individual_identity_per_individual_fast,
    copy_individual_representation,
    copy_individual_sync,
    copy_roles_sync,
    get_individual_representation_per_program_by_old_individual_id,
    migrate_data_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.migrate_grievance_for_sync import (
    handle_extra_data,
    handle_individual_data,
    handle_role_reassign_data,
    migrate_feedback,
    migrate_grievance_to_representations_per_business_area,
    migrate_messages,
)

logger = logging.getLogger(__name__)


MODEL_CLASS_UPDATE_DATE_COMPARE_FIELD_MAP = {
    HouseholdSelection: ("updated_at", "migrated_at"),
    Household: ("updated_at", "migrated_at"),
    Individual: ("updated_at", "migrated_at"),
    IndividualRoleInHousehold: ("updated_at", "migrated_at"),
    BankAccountInfo: ("updated_at", "individual__migrated_at"),
    Document: ("updated_at", "individual__migrated_at"),
    IndividualIdentity: ("modified", "individual__migrated_at"),
    GrievanceTicket: ("updated_at", "migrated_at"),
    Message: ("updated_at", "migrated_at"),
    Feedback: ("updated_at", "migrated_at"),
    FeedbackMessage: ("updated_at", "feedback__migrated_at"),
    TicketNote: ("updated_at", "ticket__migrated_at"),
    TicketComplaintDetails: ("updated_at", "ticket__migrated_at"),
    TicketSensitiveDetails: ("updated_at", "ticket__migrated_at"),
    TicketHouseholdDataUpdateDetails: ("updated_at", "ticket__migrated_at"),
    TicketIndividualDataUpdateDetails: ("updated_at", "ticket__migrated_at"),
    TicketAddIndividualDetails: ("updated_at", "ticket__migrated_at"),
    TicketDeleteIndividualDetails: ("updated_at", "ticket__migrated_at"),
    TicketDeleteHouseholdDetails: ("updated_at", "ticket__migrated_at"),
    TicketSystemFlaggingDetails: ("updated_at", "ticket__migrated_at"),
    TicketNeedsAdjudicationDetails: ("updated_at", "ticket__migrated_at"),
    TicketPaymentVerificationDetails: ("updated_at", "ticket__migrated_at"),
    TicketPositiveFeedbackDetails: ("updated_at", "ticket__migrated_at"),
    TicketNegativeFeedbackDetails: ("updated_at", "ticket__migrated_at"),
    TicketReferralDetails: ("updated_at", "ticket__migrated_at"),
    GrievanceDocument: (
        "updated_at",
        "grievance_ticket__migrated_at",
    ),
}


ONE_TO_ONE_GREVIANCE_MODELS = [
    TicketComplaintDetails,
    TicketSensitiveDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketAddIndividualDetails,
    TicketDeleteIndividualDetails,
    TicketDeleteHouseholdDetails,
    TicketSystemFlaggingDetails,
    TicketNeedsAdjudicationDetails,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketNegativeFeedbackDetails,
    TicketReferralDetails,
]


def update_representation_regular_fields(
    fields_to_update: List[str], original: models.Model, representation: models.Model
) -> None:
    for field in fields_to_update:
        logger.info(f"Updating field {field} for {representation}")
        original_field = getattr(original, field)
        if isinstance(original_field, ImageFieldFile) and original_field and original_field.name:
            try:
                file_copy = ContentFile(original_field.read())
                name_and_extension = os.path.splitext(original_field.name)
                file_copy.name = f"{name_and_extension[0]}{original.id}{name_and_extension[1]}"
                representation.file = file_copy
                setattr(representation, field, file_copy)
            except FileNotFoundError:
                logger.info(f"File not found for {original_field.name}")
        else:
            setattr(representation, field, getattr(original, field))
    if fields_to_update:
        representation.save(update_fields=fields_to_update)


def update_representation_relation_fields(
    fields_to_compare: List[str], original: models.Model, representation: models.Model
) -> None:
    relation_fields_to_update = []
    for relation_field in fields_to_compare:
        if getattr(original, relation_field) != getattr(representation, relation_field):
            relation_fields_to_update.append(relation_field)
            setattr(representation, relation_field, getattr(original, relation_field))
    if relation_fields_to_update:
        representation.save(update_fields=relation_fields_to_update)


def update_ticket_json_fields(ticket: models.Model, program: Program) -> None:
    if hasattr(ticket, "role_reassign_data"):
        ticket = handle_role_reassign_data(ticket, program)
    if hasattr(ticket, "individual_data"):
        ticket = handle_individual_data(ticket, program)  # type: ignore
    if hasattr(ticket, "extra_data"):
        handle_extra_data(ticket, program)

    ticket.save()


def update_household_representations(original: Household, representations: QuerySet[Household]) -> None:
    regular_fields_to_compare = [
        "version",
        "last_sync_at",
        "withdrawn",
        "withdrawn_date",
        "consent_sign",  # ImageField
        "consent",
        "consent_sharing",
        "residence_status",
        "country_origin",
        "country",
        "address",
        "zip_code",
        "admin_area",
        "admin1",
        "admin2",
        "admin3",
        "admin4",
        "geopoint",
        "size",
        "female_age_group_0_5_count",
        "female_age_group_6_11_count",
        "female_age_group_12_17_count",
        "female_age_group_18_59_count",
        "female_age_group_60_count",
        "pregnant_count",
        "male_age_group_0_5_count",
        "male_age_group_6_11_count",
        "male_age_group_12_17_count",
        "male_age_group_18_59_count",
        "male_age_group_60_count",
        "female_age_group_0_5_disabled_count",
        "female_age_group_6_11_disabled_count",
        "female_age_group_12_17_disabled_count",
        "female_age_group_18_59_disabled_count",
        "female_age_group_60_disabled_count",
        "male_age_group_0_5_disabled_count",
        "male_age_group_6_11_disabled_count",
        "male_age_group_12_17_disabled_count",
        "male_age_group_18_59_disabled_count",
        "male_age_group_60_disabled_count",
        "children_count",
        "male_children_count",
        "female_children_count",
        "children_disabled_count",
        "male_children_disabled_count",
        "female_children_disabled_count",
        "returnee",
        "flex_fields",
        "first_registration_date",
        "last_registration_date",
        "fchild_hoh",
        "child_hoh",
        "start",
        "deviceid",
        "name_enumerator",
        "org_enumerator",
        "org_name_enumerator",
        "village",
        "registration_method",
        "collect_individual_data",
        "currency",
        "unhcr_id",
        "user_fields",
        "kobo_asset_id",
        "row_id",
        "registration_id",
        "total_cash_received_usd",
        "total_cash_received",
        "family_id",
    ]

    relation_fields_to_compare = [
        "representatives",  # through="household.IndividualRoleInHousehold" what if changed?,
        "head_of_household",  # models.OneToOneField("Individual", related_name="heading_household", on_delete=models.CASCADE)
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        if original.head_of_household != representation.head_of_household.copied_from:
            logger.info(f"Updating field head_of_household for {representation}")
            new_head_of_household_representation = copy_individual_representation(
                program=representation.program, individual=original.head_of_household
            )
            representation.head_of_household = new_head_of_household_representation
            representation.save(update_fields=["head_of_household"])

        # representatives handled in IndividualRoleInHousehold


def update_individual_representations(original: Individual, representations: QuerySet[Individual]) -> None:
    regular_fields_to_compare = [
        "version",
        "last_sync_at",
        "duplicate",
        "duplicate_date",
        "withdrawn",
        "withdrawn_date",
        "individual_id",
        "photo",  # ImageField
        "full_name",
        "given_name",
        "middle_name",
        "family_name",
        "sex",
        "birth_date",
        "estimated_birth_date",
        "marital_status",
        "phone_no",
        "phone_no_valid",
        "phone_no_alternative",
        "phone_no_alternative_valid",
        "email",
        "payment_delivery_phone_no",
        "relationship",
        "disability",
        "work_status",
        "first_registration_date",
        "last_registration_date",
        "flex_fields",
        "user_fields",
        "enrolled_in_nutrition_programme",
        "administration_of_rutf",
        "deduplication_golden_record_status",
        "deduplication_batch_status",
        "deduplication_golden_record_results",  # ?
        "deduplication_batch_results",  # ?
        "imported_individual_id",  # ?
        "sanction_list_possible_match",
        "sanction_list_confirmed_match",
        "pregnant",
        "observed_disability",
        "seeing_disability",
        "hearing_disability",
        "physical_disability",
        "memory_disability",
        "selfcare_disability",
        "comms_disability",
        "who_answers_phone",
        "who_answers_alt_phone",
        "fchild_hoh",
        "child_hoh",
        "kobo_asset_id",
        "row_id",
        "registration_id",
        "disability_certificate_picture",  # ImageField
        "preferred_language",
        "relationship_confirmed",
        "age_at_registration",
        "vector_column",
    ]
    relation_fields_to_compare = [
        "household",
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)


def update_individual_role_in_household_representations(
    original: IndividualRoleInHousehold, representations: QuerySet[IndividualRoleInHousehold]
) -> None:
    regular_fields_to_compare = [
        "last_sync_at",
        "role",
    ]
    relation_fields_to_compare = [
        "individual",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)

        if original.individual != representation.individual.copied_from:
            if original.individual is None:
                representation.individual = None
            else:
                individual_representation = copy_individual_representation(
                    program=representation.household.program, individual=original.individual
                )
                representation.individual = individual_representation
            representation.save(update_fields=["individual"])


def update_bank_account_info_representations(
    original: BankAccountInfo, representations: QuerySet[BankAccountInfo]
) -> None:
    regular_fields_to_compare = [
        "last_sync_at",
        "bank_name",
        "bank_account_number",
        "debit_card_number",
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)


def update_document_representations(original: Document, representations: QuerySet[Document]) -> None:
    regular_fields_to_compare = [
        "last_sync_at",
        "document_number",
        "photo",  # ImageField
        "status",
        "cleared",
        "cleared_date",
        "issuance_date",
        "expiry_date",
    ]
    relation_fields_to_compare = [
        "type",  # models.ForeignKey("DocumentType", related_name="documents", on_delete=models.CASCADE)
        "country",  # models.ForeignKey("Country", related_name="documents", on_delete=models.CASCADE)
        "cleared_by",  # models.ForeignKey("account.User", null=True, on_delete=models.SET_NULL)
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_representation_relation_fields(relation_fields_to_compare, original, representation)


def update_individual_identity_representations(
    original: IndividualIdentity, representations: QuerySet[IndividualIdentity]
) -> None:
    regular_fields_to_compare = [
        "number",
    ]
    relation_fields_to_compare = [
        "partner",  # models.ForeignKey("account.Partner",related_name="individual_identities",null=True,on_delete=models.PROTECT,)
        "country",  # models.ForeignKey("geo.Country", null=True, on_delete=models.PROTECT)
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_representation_relation_fields(relation_fields_to_compare, original, representation)


def update_grievance_ticket_representations(
    original: GrievanceTicket, representations: QuerySet[GrievanceTicket]
) -> None:
    regular_fields_to_compare = [
        "user_modified",
        "last_notification_sent",
        "status",
        "category",
        "issue_type",
        "description",
        "area",
        "language",
        "consent",
        "extras",
        "ignored",
        "household_unicef_id",
        "priority",
        "urgency",
        "comments",
    ]
    relation_fields_to_compare = [
        "assigned_to",
        "admin2",
        "partner",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_representation_relation_fields(relation_fields_to_compare, original, representation)

        # sync linked "linked_tickets" = models.ManyToManyField('self', blank=True)"
        linked_tickets_ids = list(
            original.linked_tickets(manager="default_for_migrations_fix").distinct().values_list("pk", flat=True)
        )
        linked_tickets = [
            GrievanceTicketThrough(main_ticket=representation, linked_ticket_id=lt) for lt in linked_tickets_ids
        ]
        linked_tickets.extend(
            [GrievanceTicketThrough(linked_ticket=representation, main_ticket_id=lt) for lt in linked_tickets_ids]
        )
        linked_tickets.extend(
            [
                GrievanceTicketThrough(main_ticket=representation, linked_ticket_id=original.id),
                GrievanceTicketThrough(linked_ticket=representation, main_ticket_id=original.id),
            ]
        )

        GrievanceTicketThrough.objects.bulk_create(linked_tickets, ignore_conflicts=True)


def update_ticket_note_representations(original: TicketNote, representations: QuerySet[TicketNote]) -> None:
    regular_fields_to_compare = [
        "description",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)


def update_message_representations(original: Message, representations: QuerySet[Message]) -> None:
    regular_fields_to_compare = [
        "title",
        "body",
        "number_of_recipients",
        "sampling_type",
        "full_list_arguments",
        "random_sampling_arguments",
        "sample_size",
    ]
    relation_fields_to_compare = [
        "households",
        "target_population",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        # Only create so no need to track related fields


def update_feedback_representations(original: Feedback, representations: QuerySet[Feedback]) -> None:
    regular_fields_to_compare = [
        "issue_type",
        "description",
        "comments",
        "area",
        "language",
        "consent",
    ]
    relation_fields_to_compare = [
        "household_lookup",  # "household.Household",
        "individual_lookup",  # "household.Individual",
        "admin2",  # models.ForeignKey("geo.Area"
        "linked_grievance",  # can not be changed
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_representation_relation_fields(["admin2"], original, representation)

        original_individual_lookup = original.individual_lookup
        representation_individual_lookup = (
            representation.individual_lookup and representation.individual_lookup.copied_from
        )

        if original_individual_lookup != representation_individual_lookup:
            if original.individual_lookup is None:
                representation.individual_lookup = None
            else:
                representation.individual_lookup = (
                    original.individual_lookup.copied_to(manager="original_and_repr_objects")
                    .filter(program=representation.program)
                    .first()
                )
            representation.save(update_fields=["individual_lookup"])

        original_household_lookup = original.household_lookup
        representation_household_lookup = (
            representation.household_lookup and representation.household_lookup.copied_from
        )

        if original_household_lookup != representation_household_lookup:
            if original.household_lookup is None:
                representation.household_lookup = None
            else:
                representation.household_lookup = (
                    original.household_lookup.copied_to(manager="original_and_repr_objects")
                    .filter(program=representation.program)
                    .first()
                )
            representation.save(update_fields=["household_lookup"])


def update_feedback_message_representations(
    original: FeedbackMessage, representations: QuerySet[FeedbackMessage]
) -> None:
    regular_fields_to_compare = [
        "description",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)


def update_ticket_payment_details_representations(
    original: Union[TicketComplaintDetails, TicketSensitiveDetails],
    representations: QuerySet[Union[TicketComplaintDetails, TicketSensitiveDetails]],
) -> None:
    relation_fields_to_compare = [
        "payment_object_id",
        "payment_content_type",  # models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    ]
    for representation in representations:
        update_representation_relation_fields(relation_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


def update_ticket_household_data_update_details_representations(
    original: TicketHouseholdDataUpdateDetails, representations: QuerySet[TicketHouseholdDataUpdateDetails]
) -> None:
    regular_fields_to_compare = [
        "household_data",
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


def update_ticket_individual_data_update_details_representations(
    original: TicketIndividualDataUpdateDetails, representations: QuerySet[TicketIndividualDataUpdateDetails]
) -> None:
    regular_fields_to_compare = [
        # "individual_data", # handled in update_ticket_json_fields
        # "role_reassign_data", # handled in update_ticket_json_fields
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


def update_ticket_add_individual_details_representations(
    original: TicketAddIndividualDetails, representations: QuerySet[TicketAddIndividualDetails]
) -> None:
    regular_fields_to_compare = [
        # "individual_data", # handled in update_ticket_json_fields
        "approve_status"
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


def update_ticket_delete_individual_details_representations(
    original: TicketDeleteIndividualDetails, representations: QuerySet[TicketDeleteIndividualDetails]
) -> None:
    regular_fields_to_compare = [
        # "role_reassign_data", # handled in update_ticket_json_fields
        "approve_status"
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


def update_ticket_delete_household_details_representations(
    original: TicketDeleteHouseholdDetails, representations: QuerySet[TicketDeleteHouseholdDetails]
) -> None:
    regular_fields_to_compare = [
        # "role_reassign_data", # handled in update_ticket_json_fields
        "approve_status"
    ]
    relation_fields_to_compare = [
        "reason_household",
    ]

    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        original_reason_household = original.reason_household
        representation_reason_household = (
            representation.reason_household and representation.reason_household.copied_from
        )
        if original_reason_household != representation_reason_household:
            if original.reason_household is None:
                representation.reason_household = None
            else:
                representation.reason_household = (
                    original.reason_household.copied_to(manager="original_and_repr_objects")
                    .filter(program=representation.program)
                    .first()
                )
            representation.save(update_fields=["reason_household"])

        update_ticket_json_fields(representation, representation.program)


def update_ticket_system_flagging_details_representations(
    original: TicketSystemFlaggingDetails, representations: QuerySet[TicketSystemFlaggingDetails]
) -> None:
    regular_fields_to_compare = [
        "approve_status",
        # "role_reassign_data", # handled in update_ticket_json_fields
    ]
    relation_fields_to_compare = [
        "golden_records_individual",  # models.ForeignKey("household.Individual", on_delete=models.CASCADE)
        "sanction_list_individual",  # "sanction_list.SanctionListIndividual",
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)

        if original.golden_records_individual != representation.golden_records_individual.copied_from:
            if original.golden_records_individual is None:
                representation.golden_records_individual = None
            else:
                representation.golden_records_individual = (
                    original.golden_records_individual.copied_to(manager="original_and_repr_objects")
                    .filter(program=representation.program)
                    .first()
                )
            representation.save(update_fields=["golden_records_individual"])

        if original.sanction_list_individual != representation.sanction_list_individual.copied_from:
            representation.sanction_list_individual = original.sanction_list_individual
            representation.save(update_fields=["sanction_list_individual"])

        update_ticket_json_fields(representation, representation.program)


def update_ticket_needs_adjudication_details_representations(
    original: TicketNeedsAdjudicationDetails, representations: QuerySet[TicketNeedsAdjudicationDetails]
) -> None:
    regular_fields_to_compare = [
        "is_multiple_duplicates_version",
        # "role_reassign_data", # handled in update_ticket_json_fields
        # "extra_data",  # handled in update_ticket_json_fields
        "score_min",
        "score_max",
        "is_cross_area",
    ]
    relation_fields_fk_to_compare = [
        "golden_records_individual",  # models.ForeignKey("household.Individual", on_delete=models.CASCADE)
        "possible_duplicate",  # models.ForeignKey("household.Individual", on_delete=models.CASCADE)
        "selected_individual",  # models.ForeignKey("household.Individual", on_delete=models.CASCADE)
    ]
    relation_fields_m2m_to_compare = [
        "possible_duplicates",  # models.ManyToManyField("household.Individual", related_name="possible_duplicates")
        "selected_individuals",  # models.ManyToManyField("household.Individual", related_name="selected_individuals")
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)

        for field in relation_fields_fk_to_compare:
            original_field = getattr(original, field)
            representation_original_field = (
                getattr(representation, field, None) and getattr(representation, field).copied_from
            )
            if original_field != representation_original_field:
                if getattr(original, field) is None:
                    setattr(representation, field, None)
                else:
                    setattr(
                        representation,
                        field,
                        getattr(original, field)
                        .copied_to(manager="original_and_repr_objects")
                        .filter(program=representation.program)
                        .first(),
                    )
                representation.save(update_fields=["field"])

        for field in relation_fields_m2m_to_compare:
            original_field = getattr(original, field)
            representation_original_field = (
                getattr(representation, field, None) and getattr(representation, field).copied_from
            )

            if original_field != representation_original_field:
                if getattr(original, field) is None:
                    setattr(representation, field, None)
                else:
                    setattr(
                        representation,
                        field,
                        getattr(original, field)
                        .copied_to(manager="original_and_repr_objects")
                        .filter(program=representation.program)
                        .first(),
                    )
                representation.save(update_fields=["field"])


def update_ticket_payment_verification_details_representations(
    original: TicketPaymentVerificationDetails, representations: QuerySet[TicketPaymentVerificationDetails]
) -> None:
    regular_fields_to_compare = [
        "payment_verification_status",
        "new_status",
        "old_received_amount",
        "new_received_amount",
        "approve_status",
    ]
    relation_fields_to_compare = [
        "payment_verifications",  # cannot change
        "payment_verification",  # cannot change
    ]
    for representation in representations:
        update_representation_regular_fields(regular_fields_to_compare, original, representation)
        update_ticket_json_fields(representation, representation.program)


MODEL_CLASS_UPDATE_FUNCTION_MAP = {
    HouseholdSelection: lambda x, y: None,  # no regular fields to update
    Household: update_household_representations,
    Individual: update_individual_representations,
    IndividualRoleInHousehold: update_individual_role_in_household_representations,
    BankAccountInfo: update_bank_account_info_representations,
    Document: update_document_representations,
    IndividualIdentity: update_individual_identity_representations,
    GrievanceTicket: update_grievance_ticket_representations,
    Message: update_message_representations,
    Feedback: update_feedback_representations,
    FeedbackMessage: update_feedback_message_representations,
    TicketComplaintDetails: update_ticket_payment_details_representations,
    TicketSensitiveDetails: update_ticket_payment_details_representations,
    TicketHouseholdDataUpdateDetails: update_ticket_household_data_update_details_representations,
    TicketIndividualDataUpdateDetails: update_ticket_individual_data_update_details_representations,
    TicketAddIndividualDetails: update_ticket_add_individual_details_representations,
    TicketDeleteIndividualDetails: update_ticket_delete_individual_details_representations,
    TicketDeleteHouseholdDetails: update_ticket_delete_household_details_representations,
    TicketSystemFlaggingDetails: update_ticket_system_flagging_details_representations,
    TicketNeedsAdjudicationDetails: update_ticket_needs_adjudication_details_representations,
    TicketPaymentVerificationDetails: update_ticket_payment_verification_details_representations,
    TicketPositiveFeedbackDetails: lambda x, y: None,  # no regular fields to update
    TicketNegativeFeedbackDetails: lambda x, y: None,  # no regular fields to update
    TicketReferralDetails: lambda x, y: None,  # no regular fields to update
    TicketNote: update_ticket_note_representations,
}


def sync_representations() -> None:
    for business_area in BusinessArea.objects.all():
        logger.info("----- NEW BUSINESS AREA -----")
        logger.info(f"Handling business area: {business_area}")
        sync_representations_per_business_area(business_area=business_area)


def sync_representations_per_business_area(business_area: BusinessArea) -> None:
    for model, compare_fields in MODEL_CLASS_UPDATE_DATE_COMPARE_FIELD_MAP.items():
        logger.info(f"Handling MODEL: {model}")
        sync_new_objects(business_area, model)
        sync_removed_objects(business_area, model)
        sync_modified_objects(business_area, model, compare_fields)


def sync_modified_objects(business_area: BusinessArea, model: Any, compare_fields: Tuple[str, str]) -> None:
    logger.info(f"Handling modified objects for model: {model}")

    if model == GrievanceDocument:
        modified_original_objects = model.objects.filter(
            **{
                "grievance_ticket__business_area": business_area,
                "grievance_ticket__copied_to__isnull": False,
                "grievance_ticket__is_original": True,
                "grievance_ticket__is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    elif model == FeedbackMessage:
        modified_original_objects = model.objects.filter(
            **{
                "feedback__business_area": business_area,
                "feedback__copied_to__isnull": False,
                "feedback__is_original": True,
                "feedback__is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    elif model in ONE_TO_ONE_GREVIANCE_MODELS + [TicketNote]:
        modified_original_objects = model.objects.filter(
            **{
                "ticket__business_area": business_area,
                "ticket__copied_to__isnull": False,
                "ticket__is_original": True,
                "ticket__is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    elif model == IndividualRoleInHousehold:
        modified_original_objects = model.original_and_repr_objects.filter(
            **{
                "household__business_area": business_area,
                "copied_to__isnull": False,
                "is_original": True,
                "is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    elif model == HouseholdSelection:
        return  # only create/delete

    elif model == GrievanceTicket:
        modified_original_objects = model.default_for_migrations_fix.filter(
            **{
                "business_area": business_area,
                "copied_to__isnull": False,
                "is_original": True,
                "is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    elif model in [BankAccountInfo, Document, IndividualIdentity]:
        modified_original_objects = model.original_and_repr_objects.filter(
            **{
                "individual__business_area": business_area,
                "copied_to__isnull": False,
                "is_original": True,
                "is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    else:
        modified_original_objects = model.original_and_repr_objects.filter(
            **{
                "business_area": business_area,
                "copied_to__isnull": False,
                "is_original": True,
                "is_migration_handled": True,
                compare_fields[0] + "__gt": models.F(compare_fields[1]),
            }
        )

    logger.info(f"{model} Modified originals count: {modified_original_objects.count()}")

    for modified_object in modified_original_objects:
        if model in ONE_TO_ONE_GREVIANCE_MODELS:
            ticket_representations = modified_object.ticket.copied_to(manager="default_for_migration_fix").all()
            related_name = model._meta.get_field("ticket").remote_field.get_accessor_name()
            representations = model.objects.get(
                id__in=ticket_representations.values_list(related_name, flat=True)
            ).prefetch_related(related_name)

        elif model == FeedbackMessage:
            feedback_representations = modified_object.feedback.copied_to(manager="original_and_repr_objects").all()
            representations = FeedbackMessage.objects.filter(
                id__in=feedback_representations.values_list("feedback_messages", flat=True),
                created_at=modified_object.created_at,
            )

        elif model == GrievanceDocument:
            ticket_representation = modified_object.greivance_ticket.copied_to(
                manager="original_and_repr_objects"
            ).all()
            representations = GrievanceDocument.objects.filter(
                id__in=ticket_representation.values_list("documents", flat=True),
                created_at=modified_object.created_at,
            )

        elif model == TicketNote:
            ticket_representation = modified_object.ticket.copied_to(manager="default_for_migrations_fix").all()
            representations = TicketNote.objects.filter(
                id__in=ticket_representation.values_list("ticket_notes", flat=True),
                created_at=modified_object.created_at,
            )

        elif model == GrievanceTicket:
            representations = modified_object.copied_to(manager="default_for_migrations_fix").all()

        else:
            representations = modified_object.copied_to(manager="original_and_repr_objects").all()

        logger.info(f"Updating {representations.count()} representations for {modified_object}")
        MODEL_CLASS_UPDATE_FUNCTION_MAP[model](modified_object, representations)  # type: ignore


def sync_removed_objects(business_area: BusinessArea, model: Any) -> None:
    logger.info(f"Handling removed objects for model: {model}")

    related_objects_to_remove = None

    if model in ONE_TO_ONE_GREVIANCE_MODELS + [FeedbackMessage, TicketNote]:
        return  # CASCADE

    elif model == HouseholdSelection:
        return  # handled in removed Household

    if model == IndividualRoleInHousehold:
        q = Q(copied_from__isnull=True) | Q(copied_from__is_removed=True)
        filter_kwargs = dict(
            household__business_area=business_area,
            is_original=False,
        )
        representations_of_removed_objects = model.original_and_repr_objects.filter(q, **filter_kwargs)

    elif model in [BankAccountInfo, Document, IndividualIdentity]:
        q = Q(copied_from__isnull=True) | Q(copied_from__is_removed=True)
        filter_kwargs = dict(
            individual__business_area=business_area,
            is_original=False,
        )
        representations_of_removed_objects = model.original_and_repr_objects.filter(q, **filter_kwargs)

    elif model in [Message, Feedback]:
        q = Q(copied_from__isnull=True)
        filter_kwargs = dict(
            business_area=business_area,
            is_original=False,
        )
        representations_of_removed_objects = model.original_and_repr_objects.filter(q, **filter_kwargs)

    elif model == GrievanceTicket:
        filter_kwargs = dict(
            copied_from__isnull=True,
            business_area=business_area,
            is_original=False,
        )
        representations_of_removed_objects = model.default_for_migrations_fix.filter(**filter_kwargs)
        related_objects_to_remove_ids = representations_of_removed_objects.values_list(
            "support_documents__id", flat=True
        )
        related_objects_to_remove = GrievanceDocument.objects.filter(id__in=related_objects_to_remove_ids)

    elif model == GrievanceDocument:
        original_grievance_tickets_with_documents = GrievanceTicket.default_for_migrations_fix.filter(
            business_area=business_area,
            copied_to__isnull=False,
            is_original=True,
            is_migration_handled=True,
            support_documents__isnull=False,
        ).distinct()

        orphan_documents_representation_ids = []
        for original_grievance_ticket in original_grievance_tickets_with_documents:
            original_documents = list(original_grievance_ticket.support_documents.all())
            representations = original_grievance_ticket.copied_to(manager="default_for_migrations_fix").all()
            for representation in representations:
                if representation.support_documents.count() != len(original_documents):
                    # delete the orphan representations by created_at
                    orphan_documents = representation.support_documents.exclude(
                        created_at__in=[d.created_at for d in original_documents]
                    )
                    if orphan_documents.exists():
                        orphan_documents_representation_ids.extend(list(orphan_documents.values_list("id", flat=True)))

        representations_of_removed_objects = model.objects.filter(id__in=orphan_documents_representation_ids)

    else:
        q = Q(copied_from__isnull=True) | Q(copied_from__is_removed=True)
        filter_kwargs = dict(
            business_area=business_area,
            is_original=False,
        )
        representations_of_removed_objects = model.original_and_repr_objects.filter(q, **filter_kwargs)

    removed_objects_count = representations_of_removed_objects.count()
    logger.info(f"Representations to be removed count: {removed_objects_count}")
    if related_objects_to_remove:
        logger.info(
            f"Representations related objects {related_objects_to_remove.model} to be removed count: {related_objects_to_remove.count()}"
        )
        related_objects_to_remove.delete()
    representations_of_removed_objects.delete()


def sync_new_objects(business_area: BusinessArea, model: Any) -> None:
    logger.info(f"Handling new objects for model: {model}")
    originals_manager = "default_for_migrations_fix" if model == GrievanceTicket else "original_and_repr_objects"
    if model in ONE_TO_ONE_GREVIANCE_MODELS:
        return  # handled in new GrievanceTicket

    if model == HouseholdSelection:
        filter_kwargs = dict(
            household__business_area=business_area,
            is_original=True,
            is_migration_handled=False,
        )

    elif model == Individual:
        filter_kwargs = dict(
            business_area=business_area,
            copied_to__isnull=True,
            is_original=True,
            is_migration_handled=False,
        )

    elif model == IndividualRoleInHousehold:
        filter_kwargs = dict(
            household__business_area=business_area,
            is_original=True,
            is_migration_handled=False,
            copied_to__isnull=True,
        )

    elif model in [BankAccountInfo, Document, IndividualIdentity]:
        filter_kwargs = dict(
            individual__business_area=business_area,
            individual__is_original=True,
            individual__is_migration_handled=True,
            copied_to__isnull=True,
            is_original=True,
        )

    elif model == FeedbackMessage:
        originals_manager = "objects"
        filter_kwargs = dict(
            feedback__business_area=business_area,
            feedback__is_original=True,
            feedback__is_migration_handled=True,
            created_at__gt=models.F("feedback__migrated_at"),
        )

    elif model == TicketNote:
        originals_manager = "objects"
        filter_kwargs = dict(
            ticket__business_area=business_area,
            ticket__is_original=True,
            ticket__is_migration_handled=True,
            created_at__gt=models.F("ticket__migrated_at"),
        )

    elif model == GrievanceDocument:
        originals_manager = "objects"
        filter_kwargs = dict(
            grievance_ticket__business_area=business_area,
            grievance_ticket__is_original=True,
            grievance_ticket__is_migration_handled=True,
            created_at__gt=models.F("grievance_ticket__migrated_at"),
        )

    else:
        filter_kwargs = dict(
            business_area=business_area,
            copied_to__isnull=True,
            is_original=True,
            is_migration_handled=False,
        )

    new_objects = getattr(model, originals_manager).filter(**filter_kwargs).order_by("id")
    new_objects_count = new_objects.count()
    logger.info(f"New objects count: {new_objects_count}")

    if new_objects_count:
        if model == HouseholdSelection:
            migrate_data_to_representations_per_business_area(business_area)

        elif model == Household:
            # this should be handled in HouseholdSelection
            return

        elif model == Individual:
            copy_individual_sync(list(new_objects.values_list("id", flat=True)))

        elif model == IndividualRoleInHousehold:
            copy_roles_sync(list(new_objects.values_list("id", flat=True)))

        elif model == BankAccountInfo:
            bank_accounts_info_to_create = []
            for obj in new_objects:
                programs = list(
                    obj.individual.copied_to(manager="original_and_repr_objects")
                    .all()
                    .values_list("program", flat=True)
                )
                for program in programs:
                    bank_account_info_to_create = copy_bank_account_info_per_individual_fast(
                        [obj],
                        get_individual_representation_per_program_by_old_individual_id(
                            program=program,
                            old_individual_id=obj.individual_id,
                        ),  # type: ignore
                    )
                    bank_accounts_info_to_create.extend(bank_account_info_to_create)
            if bank_accounts_info_to_create:
                BankAccountInfo.objects.bulk_create(bank_accounts_info_to_create, ignore_conflicts=True)

        elif model == Document:
            documents = []
            for obj in new_objects:
                programs = list(
                    obj.individual.copied_to(manager="original_and_repr_objects")
                    .all()
                    .values_list("program", flat=True)
                )
                for program in programs:
                    document = copy_document_per_individual_fast(
                        [obj],
                        get_individual_representation_per_program_by_old_individual_id(
                            program=program,
                            old_individual_id=obj.individual_id,
                        ),  # type: ignore
                    )
                    documents.extend(document)
            if documents:
                Document.objects.bulk_create(documents, ignore_conflicts=True)

        elif model == IndividualIdentity:
            individual_identities_to_create = []
            for obj in new_objects:
                programs = list(
                    obj.individual.copied_to(manager="original_and_repr_objects")
                    .all()
                    .values_list("program", flat=True)
                )
                for program in programs:
                    individual_identity_to_create = copy_individual_identity_per_individual_fast(
                        [obj],
                        get_individual_representation_per_program_by_old_individual_id(
                            program=program,
                            old_individual_id=obj.individual_id,
                        ),  # type: ignore
                    )
                    individual_identities_to_create.extend(individual_identity_to_create)
            if individual_identities_to_create:
                IndividualIdentity.objects.bulk_create(individual_identities_to_create, ignore_conflicts=True)

        elif model == GrievanceTicket:
            migrate_grievance_to_representations_per_business_area(business_area=business_area)

        elif model == Message:
            migrate_messages(business_area=business_area)

        elif model == Feedback:
            migrate_feedback(business_area=business_area)

        elif model == FeedbackMessage:
            feedback_messages_to_create = []
            for obj in new_objects:
                for feedback_representation in obj.feedback.copied_to(manager="original_and_repr_objects").all():
                    message_copy = copy.deepcopy(obj)
                    message_copy.pk = None
                    message_copy.feedback = feedback_representation
                    feedback_messages_to_create.append(message_copy)
            if feedback_messages_to_create:
                FeedbackMessage.objects.bulk_create(feedback_messages_to_create, ignore_conflicts=True)

        elif model == TicketNote:
            ticket_notes_to_create = []
            for obj in new_objects:
                for ticket_representation in obj.ticket.copied_to(manager="default_for_migrations_fix").all():
                    note_copy = copy.deepcopy(obj)
                    note_copy.pk = None
                    note_copy.ticket = ticket_representation
                    ticket_notes_to_create.append(note_copy)
            if ticket_notes_to_create:
                TicketNote.objects.bulk_create(ticket_notes_to_create, ignore_conflicts=True)

        elif model == GrievanceDocument:
            documents_to_create = []
            for obj in new_objects:
                for ticket_representation in obj.grievance_ticket.copied_to(manager="default_for_migrations_fix").all():
                    document_copy = copy.deepcopy(obj)
                    document_copy.pk = None
                    document_copy.grievance_ticket = ticket_representation
                    documents_to_create.append(document_copy)
            if documents_to_create:
                GrievanceDocument.bulk_create(documents_to_create, ignore_conflicts=True)
