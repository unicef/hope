from strategy_field.registry import Registry


class AuroraProcessor:
    def label(self) -> str:
        return self.__class__.__name__


registry = Registry(AuroraProcessor)


# Looks unused, but Registration.rdi_parser may store this class by dotted path.
class DefaultProcessor(AuroraProcessor):
    pass
