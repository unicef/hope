from datetime import datetime
from typing import Any, Dict

from django.core.exceptions import ValidationError
from django.db import transaction

import graphene

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.scalars import BigInt
from hct_mis_api.apps.core.utils import (
    check_concurrency_version_in_mutation,
    decode_id_string,
    decode_id_string_required,
)
from hct_mis_api.apps.core.validators import (
    CommonValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
)
from hct_mis_api.apps.periodic_data_update.service.flexible_attribute_service import (
    FlexibleAttributeForPDUService,
)
from hct_mis_api.apps.program.celery_tasks import (
    copy_program_task,
    populate_pdu_new_rounds_with_null_values_task,
)
from hct_mis_api.apps.program.inputs import (
    CopyProgramInput,
    CreateProgramInput,
    UpdateProgramInput,
    UpdateProgramPartnersInput,
)
from hct_mis_api.apps.program.models import BeneficiaryGroup, Program, ProgramCycle
from hct_mis_api.apps.program.schema import ProgramNode
from hct_mis_api.apps.program.utils import (
    copy_program_object,
    create_program_partner_access,
    remove_program_partner_access,
)
from hct_mis_api.apps.program.validators import (
    ProgramDeletionValidator,
    ProgrammeCodeValidator,
    ProgramValidator,
)
from hct_mis_api.apps.registration_datahub.services.biometric_deduplication import (
    BiometricDeduplicationService,
)
from hct_mis_api.apps.utils.mutations import ValidationErrorMutationMixin


class CreateProgram(
    CommonValidator,
    ProgrammeCodeValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
    PermissionMutation,
    ValidationErrorMutationMixin,
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CreateProgramInput(required=True)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CreateProgram":
        business_area_slug = program_data.pop("business_area_slug", None)
        business_area = BusinessArea.objects.get(slug=business_area_slug)

        cls.has_permission(info, Permissions.PROGRAMME_CREATE, business_area)

        if not (data_collecting_type_code := program_data.pop("data_collecting_type_code", None)):
            raise ValidationError("DataCollectingType is required for creating new Program")
        data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)
        if not (beneficiary_group_id := program_data.pop("beneficiary_group", None)):
            raise ValidationError("Beneficiary Group is required for creating new Program")
        beneficiary_group = BeneficiaryGroup.objects.get(id=beneficiary_group_id)
        partner_access = program_data.get("partner_access", [])
        partners_data = program_data.pop("partners", [])
        pdu_fields = program_data.pop("pdu_fields", None)
        programme_code = program_data.get("programme_code", "")
        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code

        partner = info.context.user.partner

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=(
                datetime.combine(program_data["end_date"], datetime.min.time())
                if program_data.get("end_date")
                else None
            ),
            data_collecting_type=data_collecting_type,
            business_area=business_area,
            programme_code=programme_code,
            partners_data=partners_data,
            partner_access=partner_access,
            partner=partner,
        )

        program = Program(
            **program_data,
            status=Program.DRAFT,
            business_area=business_area,
            data_collecting_type=data_collecting_type,
            beneficiary_group=beneficiary_group,
        )
        if not program.programme_code:
            program.programme_code = program.generate_programme_code()
        program.slug = program.generate_slug()

        program.full_clean()
        program.save()
        ProgramCycle.objects.create(
            program=program,
            start_date=program.start_date,
            end_date=None,
            status=ProgramCycle.DRAFT,
            created_by=info.context.user,
        )
        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, partner_access)

        if pdu_fields is not None:
            FlexibleAttributeForPDUService(program, pdu_fields).create_pdu_flex_attributes()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)
        return CreateProgram(program=program)


class UpdateProgram(
    ProgramValidator,
    ProgrammeCodeValidator,
    DataCollectingTypeValidator,
    PartnersDataValidator,
    PermissionMutation,
    ValidationErrorMutationMixin,
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramInput()
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict, **kwargs: Any) -> "UpdateProgram":
        program_id = decode_id_string(program_data.pop("id", None))
        program = Program.objects.select_for_update().get(id=program_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), program)
        old_program = Program.objects.get(id=program_id)
        business_area = program.business_area
        pdu_fields = program_data.pop("pdu_fields", None)
        programme_code = program_data.get("programme_code", "")
        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code

        # status update permissions if status is passed
        status_to_set = program_data.get("status")
        if status_to_set and program.status != status_to_set:
            if status_to_set == Program.ACTIVE:
                cls.has_permission(info, Permissions.PROGRAMME_ACTIVATE, business_area)
            elif status_to_set == Program.FINISHED:
                cls.has_permission(info, Permissions.PROGRAMME_FINISH, business_area)

        data_collecting_type_code = program_data.pop("data_collecting_type_code", None)
        data_collecting_type = old_program.data_collecting_type
        if data_collecting_type_code and data_collecting_type_code != data_collecting_type.code:
            data_collecting_type = DataCollectingType.objects.get(code=data_collecting_type_code)

        # permission if updating any other fields
        if [k for k, v in program_data.items() if k != "status"]:
            cls.has_permission(info, Permissions.PROGRAMME_UPDATE, business_area)
        cls.validate(
            program_data=program_data,
            program=program,
            start_date=program_data.get("start_date"),
            end_date=program_data.get("end_date"),
            data_collecting_type=data_collecting_type,
            business_area=business_area,
            programme_code=programme_code,
            excluded_validators="validate_partners_data",
        )
        if program.status == Program.FINISHED:
            # Only reactivation is possible
            if status_to_set != Program.ACTIVE or len(program_data) > 1:
                raise ValidationError("You cannot change finished program")
        if beneficiary_group_id := program_data.pop("beneficiary_group", None):
            beneficiary_group = BeneficiaryGroup.objects.get(id=beneficiary_group_id)
            if old_program.registration_imports.exists() and old_program.beneficiary_group != beneficiary_group:
                raise ValidationError("You cannot update a program's Beneficiary Group if it has imported population.")
            program_data["beneficiary_group"] = beneficiary_group

        if data_collecting_type_code:
            program.data_collecting_type = data_collecting_type

        for attrib, value in program_data.items():
            if hasattr(program, attrib):
                setattr(program, attrib, value)
        program.full_clean()
        program.save()

        if status_to_set == Program.FINISHED and program.biometric_deduplication_enabled:
            BiometricDeduplicationService().delete_deduplication_set(program)

        if pdu_fields is not None:
            FlexibleAttributeForPDUService(program, pdu_fields).update_pdu_flex_attributes_in_program_update()
            populate_pdu_new_rounds_with_null_values_task.delay(program_id)

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, old_program, program)
        return UpdateProgram(program=program)


class UpdateProgramPartners(
    PartnersDataValidator,
    PermissionMutation,
    ValidationErrorMutationMixin,
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = UpdateProgramPartnersInput()
        version = BigInt(required=False)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict, **kwargs: Any) -> "UpdateProgram":
        program_id = decode_id_string(program_data.pop("id", None))
        program = Program.objects.select_for_update().get(id=program_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), program)
        old_program = Program.objects.get(id=program_id)
        business_area = program.business_area
        partners_data = program_data.pop("partners", [])
        partner = info.context.user.partner
        partner_access = program_data.get("partner_access", None)
        old_partner_access = old_program.partner_access

        cls.has_permission(info, Permissions.PROGRAMME_UPDATE, business_area)

        cls.validate_partners_data(
            partners_data=partners_data,
            partner_access=partner_access,
            partner=partner,
        )

        program.partner_access = partner_access

        # update partner access for ALL_PARTNERS_ACCESS type if it was not changed but the partners need to be refetched
        if partner_access == old_partner_access and partner_access == Program.ALL_PARTNERS_ACCESS:
            create_program_partner_access([], program, partner_access)
        # update partner access only for SELECTED_PARTNERS_ACCESS type, since update to NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            partners_data = create_program_partner_access(partners_data, program, partner_access)
            remove_program_partner_access(partners_data, program)
        program.save()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, old_program, program)
        return UpdateProgram(program=program)


class DeleteProgram(ProgramDeletionValidator, PermissionMutation):
    ok = graphene.Boolean()

    class Arguments:
        program_id = graphene.String(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> "DeleteProgram":
        decoded_id = decode_id_string(kwargs.get("program_id"))
        program = Program.objects.get(id=decoded_id)
        old_program = Program.objects.get(id=decoded_id)

        cls.has_permission(info, Permissions.PROGRAMME_REMOVE, program.business_area)

        cls.validate(program=program)

        program.delete()
        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, old_program, program)
        return cls(ok=True)


class CopyProgram(
    CommonValidator, ProgrammeCodeValidator, PartnersDataValidator, PermissionMutation, ValidationErrorMutationMixin
):
    program = graphene.Field(ProgramNode)

    class Arguments:
        program_data = CopyProgramInput(required=True)

    @classmethod
    @transaction.atomic
    @is_authenticated
    def processed_mutate(cls, root: Any, info: Any, program_data: Dict) -> "CopyProgram":
        program_id = decode_id_string_required(program_data.pop("id"))
        partners_data = program_data.pop("partners", [])
        partner_access = program_data.get("partner_access", [])
        business_area = Program.objects.get(id=program_id).business_area
        programme_code = program_data.get("programme_code", "")
        pdu_fields = program_data.pop("pdu_fields", None)
        partner = info.context.user.partner
        if programme_code:
            programme_code = programme_code.upper()
            program_data["programme_code"] = programme_code
        cls.has_permission(info, Permissions.PROGRAMME_DUPLICATE, business_area)

        cls.validate(
            start_date=datetime.combine(program_data["start_date"], datetime.min.time()),
            end_date=datetime.combine(program_data["end_date"], datetime.min.time()),
            programme_code=programme_code,
            business_area=business_area,
            partners_data=partners_data,
            partner_access=partner_access,
            partner=partner,
        )
        program = copy_program_object(program_id, program_data, info.context.user)

        # create partner access only for SELECTED_PARTNERS_ACCESS type, since NONE and ALL are handled through signal
        if partner_access == Program.SELECTED_PARTNERS_ACCESS:
            create_program_partner_access(partners_data, program, partner_access)

        transaction.on_commit(
            lambda: copy_program_task.delay(
                copy_from_program_id=program_id, new_program_id=program.id, user_id=str(info.context.user.id)
            )
        )

        if pdu_fields is not None:
            FlexibleAttributeForPDUService(program, pdu_fields).create_pdu_flex_attributes()

        log_create(Program.ACTIVITY_LOG_MAPPING, "business_area", info.context.user, program.pk, None, program)

        return CopyProgram(program=program)


class Mutations(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    update_program_partners = UpdateProgramPartners.Field()
    delete_program = DeleteProgram.Field()
    copy_program = CopyProgram.Field()
