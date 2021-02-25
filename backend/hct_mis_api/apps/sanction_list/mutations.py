import graphene
from graphene_file_upload.scalars import Upload

from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.registration_datahub.schema import XlsxRowErrorNode
from hct_mis_api.apps.registration_datahub.validators import XLSXValidator
from hct_mis_api.apps.sanction_list.celery_tasks import check_against_sanction_list_task
from hct_mis_api.apps.sanction_list.models import UploadedXLSXFile


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
    def mutate(cls, root, info, file):
        errors = cls.validate(file=file)
        if errors:
            return CheckAgainstSanctionListMutation(False, errors)

        user = info.context.user
        uploaded_file = UploadedXLSXFile.objects.create(file=file, associated_email=user.email)

        check_against_sanction_list_task.delay(
            uploaded_file_id=str(uploaded_file.id),
            original_file_name=file.name,
        )

        return CheckAgainstSanctionListMutation(True, errors)


class Mutations(graphene.ObjectType):
    check_against_sanction_list = CheckAgainstSanctionListMutation.Field()
