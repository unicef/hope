from strategy_field.registry import Registry

from ._base import BaseSanctionList


class SanctionListRegistry(Registry):
    pass


registry = SanctionListRegistry(BaseSanctionList)
