import graphene


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
