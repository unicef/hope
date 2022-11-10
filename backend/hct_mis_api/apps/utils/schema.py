import logging

from django.core.files.storage import default_storage

import graphene

from hct_mis_api.apps.core.field_attributes.core_fields_attributes import TYPE_IMAGE
from hct_mis_api.apps.core.models import FlexibleAttribute

logger = logging.getLogger(__name__)


class Arg(graphene.Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class _DetailedDatasetsNode(graphene.ObjectType):
    label = graphene.String()
    data = graphene.List(graphene.Float)


class ChartDetailedDatasetsNode(graphene.ObjectType):
    labels = graphene.List(graphene.String)
    datasets = graphene.List(_DetailedDatasetsNode)


class _DatasetsNode(graphene.ObjectType):
    data = graphene.List(graphene.Float)


class ChartDatasetNode(graphene.ObjectType):
    labels = graphene.List(graphene.String)
    datasets = graphene.List(_DatasetsNode)


class SectionTotalNode(graphene.ObjectType):
    total = graphene.Float()


class _TableTotalCashTransferredDataNode(graphene.ObjectType):
    id = graphene.String()
    admin2 = graphene.String()
    total_cash_transferred = graphene.Float()
    total_households = graphene.Int()


class TableTotalCashTransferred(graphene.ObjectType):
    data = graphene.List(_TableTotalCashTransferredDataNode)


class FlexFieldsScalar(graphene.Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        if not dt:
            return dt

        images_flex_fields_names = FlexibleAttribute.objects.filter(type=TYPE_IMAGE).values_list("name", flat=True)
        for name, value in dt.items():
            if value and name in images_flex_fields_names:
                try:
                    dt[name] = default_storage.url(value)
                except Exception as e:
                    logger.exception(e)
                    raise

        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value
