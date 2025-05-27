from typing import IO, Any

import graphene
from graphene_file_upload.scalars import Upload

from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.registration_datahub.validators import (
    XlsxException,
    XLSXValidator,
)
from hct_mis_api.apps.sanction_list.celery_tasks import check_against_sanction_list_task
from hct_mis_api.apps.sanction_list.models import UploadedXLSXFile


class XlsxRowErrorNode(graphene.ObjectType):
    row_number = graphene.Int()
    header = graphene.String()
    message = graphene.String()


class CheckAgainstSanctionListMutation(
    XLSXValidator,
    graphene.Mutation,
):
    ok = graphene.Boolean()
    errors = graphene.List(XlsxRowErrorNode)

    class Arguments:
        file = Upload(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root: Any, info: Any, file: IO) -> "CheckAgainstSanctionListMutation":
        try:
            cls.validate(file=file)
        except XlsxException as e:
            return CheckAgainstSanctionListMutation(ok=False, errors=e.errors)

        user = info.context.user
        uploaded_file = UploadedXLSXFile.objects.create(file=file, associated_email=user.email)

        check_against_sanction_list_task.delay(
            uploaded_file_id=str(uploaded_file.id),
            original_file_name=file.name,
        )

        return CheckAgainstSanctionListMutation(ok=True, errors=[])


class Mutations(graphene.ObjectType):
    check_against_sanction_list = CheckAgainstSanctionListMutation.Field()
