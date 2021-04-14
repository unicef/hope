import graphene


class BigInt(graphene.Scalar):
    """
    BigInt is an extension of the regular Int field
    that supports Integers bigger than a signed
    32-bit integer.
    """

    @classmethod
    def parse_value(cls, value):
        return int(value)

    @classmethod
    def serialize(cls, value):
        return int(value)

    @staticmethod
    def parse_literal(node):
        return int(node.value)
