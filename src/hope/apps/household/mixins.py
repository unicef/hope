class IndividualDeliveryDataMixin:
    """Mixin for getting FSP specific payment delivery data. Property names are defined in FspNameMapping.hope_name.

    Example usage of mixin, will be removed later.
    You can define attribute for retrieving specific document etc.

    @property
    def full_name_example(self) -> str:
        return self.full_name + "xxx"
    """


class HouseholdDeliveryDataMixin:
    """Mixin to get FSP specific payment delivery data. Property names are defined in FspNameMapping.hope_name.

    Example usage of mixin, will be removed later.
    You can define attribute for retrieving specific/modified household data.

    @property
    def address_example(self) -> str:
        return self.address + "xxx"
    """
