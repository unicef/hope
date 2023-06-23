from strategy_field.registry import Registry


class AuroraProcessor:
    def label(self) -> str:
        return self.__class__.__name__


registry = Registry(AuroraProcessor, label_attribute="label")


class DefaultProcessor(AuroraProcessor):
    pass
