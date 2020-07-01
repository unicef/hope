import graphene
from graphene_file_upload.scalars import Upload

from core.airflow_api import AirflowApi
from core.permissions import is_authenticated
from registration_datahub.schema import XlsxRowErrorNode
from registration_datahub.validators import XLSXValidator
from sanction_list.models import UploadedXLSXFile


class CheckAgainstSanctionListMutation(
    XLSXValidator, graphene.Mutation,
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
        uploaded_file = UploadedXLSXFile.objects.create(
            file=file, associated_email=user.email
        )

        AirflowApi.start_dag(
            dag_id="CheckAgainstSanctionList",
            context={"uploaded_file_id": str(uploaded_file.id)},
        )

        return CheckAgainstSanctionListMutation(True, errors)


class Mutations(graphene.ObjectType):
    check_against_sanction_list = CheckAgainstSanctionListMutation.Field()
