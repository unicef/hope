from strategy_field.registry import Registry


class AuroraProcessor:
    def label(self) -> str:
        return self.__class__.__name__


#
# class RegistryProcessor(Registry):
#     pass

registry = Registry(AuroraProcessor, label_attribute="label")


class DefaultProcessor(AuroraProcessor):
    pass


registry.register(DefaultProcessor)
