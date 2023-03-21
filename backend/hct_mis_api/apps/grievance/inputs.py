import graphene
from graphene_file_upload.scalars import Upload

from hct_mis_api.apps.account.schema import PartnerType, UserNode
from hct_mis_api.apps.core.schema import BusinessAreaNode
from hct_mis_api.apps.grievance.schema import GrievanceTicketNode
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.schema import PaymentRecordNode
from hct_mis_api.apps.program.schema import ProgramNode
from hct_mis_api.apps.utils.schema import Arg


class CreateTicketNoteInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    ticket = graphene.GlobalID(node=GrievanceTicketNode, required=True)


class PositiveFeedbackTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


class NegativeFeedbackTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


class GrievanceComplaintTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.List(graphene.ID)


class PaymentVerificationTicketExtras(graphene.InputObjectType):
    pass


class ReferralTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)


class SensitiveGrievanceTicketExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.List(graphene.ID)


class TicketPaymentVerificationDetailsExtras(graphene.InputObjectType):
    new_received_amount = graphene.Float()
    new_status = graphene.String()


class HouseholdUpdateDataObjectType(graphene.InputObjectType):
    admin_area_title = graphene.String()
    status = graphene.String()
    consent = graphene.Boolean()
    consent_sharing = graphene.List(graphene.String)
    residence_status = graphene.String()
    country_origin = graphene.String()
    country = graphene.String()
    size = graphene.Int()
    address = graphene.String()
    female_age_group_0_5_count = graphene.Int()
    female_age_group_6_11_count = graphene.Int()
    female_age_group_12_17_count = graphene.Int()
    female_age_group_18_59_count = graphene.Int()
    female_age_group_60_count = graphene.Int()
    pregnant_count = graphene.Int()
    male_age_group_0_5_count = graphene.Int()
    male_age_group_6_11_count = graphene.Int()
    male_age_group_12_17_count = graphene.Int()
    male_age_group_18_59_count = graphene.Int()
    male_age_group_60_count = graphene.Int()
    female_age_group_0_5_disabled_count = graphene.Int()
    female_age_group_6_11_disabled_count = graphene.Int()
    female_age_group_12_17_disabled_count = graphene.Int()
    female_age_group_18_59_disabled_count = graphene.Int()
    female_age_group_60_disabled_count = graphene.Int()
    male_age_group_0_5_disabled_count = graphene.Int()
    male_age_group_6_11_disabled_count = graphene.Int()
    male_age_group_12_17_disabled_count = graphene.Int()
    male_age_group_18_59_disabled_count = graphene.Int()
    male_age_group_60_disabled_count = graphene.Int()
    returnee = graphene.Boolean()
    fchild_hoh = graphene.Boolean()
    child_hoh = graphene.Boolean()
    start = graphene.DateTime()
    end = graphene.DateTime()
    name_enumerator = graphene.String()
    org_enumerator = graphene.String()
    org_name_enumerator = graphene.String()
    village = graphene.String()
    registration_method = graphene.String()
    collect_individual_data = graphene.String()
    currency = graphene.String()
    unhcr_id = graphene.String()
    flex_fields = Arg()


class IndividualDocumentObjectType(graphene.InputObjectType):
    country = graphene.String(required=True)
    type = graphene.String(required=True)
    number = graphene.String(required=True)
    photo = Arg()
    photoraw = Arg()


class EditIndividualDocumentObjectType(graphene.InputObjectType):
    id = graphene.Field(graphene.ID, required=True)
    country = graphene.String(required=True)
    type = graphene.String(required=True)
    number = graphene.String(required=True)
    photo = Arg()
    photoraw = Arg()


class IndividualIdentityObjectType(graphene.InputObjectType):
    country = graphene.String(required=True)
    partner = graphene.String(required=True)
    number = graphene.String(required=True)


class EditIndividualIdentityObjectType(graphene.InputObjectType):
    id = graphene.Field(graphene.ID, required=True)
    country = graphene.String(required=True)
    partner = graphene.String(required=True)
    number = graphene.String(required=True)


class BankTransferObjectType(graphene.InputObjectType):
    type = graphene.String(required=True)
    bank_name = graphene.String(required=True)
    bank_account_number = graphene.String(required=True)


class EditBankTransferObjectType(graphene.InputObjectType):
    id = graphene.Field(graphene.ID, required=True)
    type = graphene.String(required=True)
    bank_name = graphene.String(required=True)
    bank_account_number = graphene.String(required=True)


class IndividualUpdateDataObjectType(graphene.InputObjectType):
    status = graphene.String()
    full_name = graphene.String()
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String()
    birth_date = graphene.Date()
    estimated_birth_date = graphene.Boolean()
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String()
    disability = graphene.String()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String()
    documents = graphene.List(IndividualDocumentObjectType)
    documents_to_remove = graphene.List(graphene.ID)
    documents_to_edit = graphene.List(EditIndividualDocumentObjectType)
    identities = graphene.List(IndividualIdentityObjectType)
    identities_to_remove = graphene.List(graphene.ID)
    identities_to_edit = graphene.List(EditIndividualIdentityObjectType)
    payment_channels = graphene.List(BankTransferObjectType)
    payment_channels_to_edit = graphene.List(EditBankTransferObjectType)
    payment_channels_to_remove = graphene.List(graphene.ID)
    flex_fields = Arg()


class AddIndividualDataObjectType(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    given_name = graphene.String()
    middle_name = graphene.String()
    family_name = graphene.String()
    sex = graphene.String(required=True)
    birth_date = graphene.Date(required=True)
    estimated_birth_date = graphene.Boolean(required=True)
    marital_status = graphene.String()
    phone_no = graphene.String()
    phone_no_alternative = graphene.String()
    relationship = graphene.String(required=True)
    disability = graphene.Boolean()
    work_status = graphene.String()
    enrolled_in_nutrition_programme = graphene.Boolean()
    administration_of_rutf = graphene.Boolean()
    pregnant = graphene.Boolean()
    observed_disability = graphene.List(graphene.String)
    seeing_disability = graphene.String()
    hearing_disability = graphene.String()
    physical_disability = graphene.String()
    memory_disability = graphene.String()
    selfcare_disability = graphene.String()
    comms_disability = graphene.String()
    who_answers_phone = graphene.String()
    who_answers_alt_phone = graphene.String()
    role = graphene.String(required=True)
    documents = graphene.List(IndividualDocumentObjectType)
    identities = graphene.List(IndividualIdentityObjectType)
    payment_channels = graphene.List(BankTransferObjectType)
    business_area = graphene.String()
    flex_fields = Arg()


class HouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    household_data = HouseholdUpdateDataObjectType(required=True)


class IndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)
    individual_data = IndividualUpdateDataObjectType(required=True)


class AddIndividualIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)
    individual_data = AddIndividualDataObjectType(required=True)


class UpdateHouseholdDataUpdateIssueTypeExtras(graphene.InputObjectType):
    household_data = HouseholdUpdateDataObjectType(required=True)


class UpdateIndividualDataUpdateIssueTypeExtras(graphene.InputObjectType):
    individual_data = IndividualUpdateDataObjectType(required=True)


class UpdateAddIndividualIssueTypeExtras(graphene.InputObjectType):
    individual_data = AddIndividualDataObjectType(required=True)


class IndividualDeleteIssueTypeExtras(graphene.InputObjectType):
    individual = graphene.GlobalID(node=IndividualNode, required=True)


class HouseholdDeleteIssueTypeExtras(graphene.InputObjectType):
    household = graphene.GlobalID(node=HouseholdNode, required=True)


class IssueTypeExtrasInput(graphene.InputObjectType):
    household_data_update_issue_type_extras = HouseholdDataUpdateIssueTypeExtras()
    individual_data_update_issue_type_extras = IndividualDataUpdateIssueTypeExtras()
    individual_delete_issue_type_extras = IndividualDeleteIssueTypeExtras()
    household_delete_issue_type_extras = HouseholdDeleteIssueTypeExtras()
    add_individual_issue_type_extras = AddIndividualIssueTypeExtras()


class CategoryExtrasInput(graphene.InputObjectType):
    sensitive_grievance_ticket_extras = SensitiveGrievanceTicketExtras()
    grievance_complaint_ticket_extras = GrievanceComplaintTicketExtras()
    positive_feedback_ticket_extras = PositiveFeedbackTicketExtras()
    negative_feedback_ticket_extras = NegativeFeedbackTicketExtras()
    referral_ticket_extras = ReferralTicketExtras()


class CreateGrievanceTicketExtrasInput(graphene.InputObjectType):
    category = CategoryExtrasInput()
    issue_type = IssueTypeExtrasInput()


class UpdateGrievanceTicketExtrasInput(graphene.InputObjectType):
    household_data_update_issue_type_extras = UpdateHouseholdDataUpdateIssueTypeExtras()
    individual_data_update_issue_type_extras = UpdateIndividualDataUpdateIssueTypeExtras()
    add_individual_issue_type_extras = UpdateAddIndividualIssueTypeExtras()
    category = CategoryExtrasInput()
    ticket_payment_verification_details_extras = TicketPaymentVerificationDetailsExtras()


class GrievanceDocumentInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    file = Upload(required=True)


class GrievanceDocumentUpdateInput(graphene.InputObjectType):
    id = graphene.Field(graphene.ID, required=True)
    name = graphene.String(required=False)
    file = Upload(required=False)


class CreateGrievanceTicketInput(graphene.InputObjectType):
    description = graphene.String(required=True)
    assigned_to = graphene.GlobalID(node=UserNode, required=False)
    category = graphene.Int(required=True)
    issue_type = graphene.Int()
    admin = graphene.String()
    area = graphene.String()
    language = graphene.String(required=True)
    consent = graphene.Boolean(required=True)
    business_area = graphene.GlobalID(node=BusinessAreaNode, required=True)
    linked_tickets = graphene.List(graphene.ID)
    extras = CreateGrievanceTicketExtrasInput()
    priority = graphene.Int(required=False)
    urgency = graphene.Int(required=False)
    partner = graphene.Int(node=PartnerType, required=False)
    programme = graphene.ID(node=ProgramNode)
    comments = graphene.String()
    linked_feedback_id = graphene.ID()
    documentation = graphene.List(GrievanceDocumentInput)


class UpdateGrievanceTicketInput(graphene.InputObjectType):
    ticket_id = graphene.GlobalID(node=GrievanceTicketNode, required=True)
    description = graphene.String()
    assigned_to = graphene.GlobalID(node=UserNode, required=False)
    admin = graphene.String()
    area = graphene.String()
    language = graphene.String()
    linked_tickets = graphene.List(graphene.ID)
    household = graphene.GlobalID(node=HouseholdNode, required=False)
    individual = graphene.GlobalID(node=IndividualNode, required=False)
    payment_record = graphene.GlobalID(node=PaymentRecordNode, required=False)
    extras = UpdateGrievanceTicketExtrasInput()
    priority = graphene.Int(required=False)
    urgency = graphene.Int(required=False)
    partner = graphene.Int(node=PartnerType, required=False)
    programme = graphene.ID(node=ProgramNode)
    comments = graphene.String()
    documentation = graphene.List(GrievanceDocumentInput)
    documentation_to_update = graphene.List(GrievanceDocumentUpdateInput)
    documentation_to_delete = graphene.List(graphene.ID)
