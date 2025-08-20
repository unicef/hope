import factory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory


class ModifiedPaymentFactory(PaymentFactory):
    """
    A specialized factory for creating Payments that match the filtering logic
    in DashboardDataCache.refresh_data.
    """

    parent = factory.SubFactory(PaymentPlanFactory, status=factory.Iterator(["ACCEPTED", "FINISHED"]))
    status = factory.Iterator(
        [
            "Transaction Successful",
            "Distribution Successful",
            "Partially Distributed",
            "Pending",
        ]
    )
